from django.db import models
import pandas as pd
import os
import logging
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import gzip

logger = logging.getLogger(__name__)

# Create your models here.

class IpecsReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ipecs_reports/')
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    processed_data = models.JSONField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.file_name} ({self.status})"

    def get_data(self):
        """
        Returns the processed data if available, otherwise processes the file and returns the data.
        """
        if self.status == 'pending':
            self.process_file()
        
        if self.processed_data:
            return self.processed_data
        
        return self.unpack_slk()

    def process_file(self):
        """
        Process the uploaded SMDR report file.
        """
        try:
            logger.info(f"Starting to process file: {self.file_name}")
            
            # Parse the SLK format
            try:
                data = self.unpack_slk()
                logger.info(f"Successfully unpacked SLK data, got {len(data) if data else 0} rows")
                # Debug: Print first few rows of raw data
                for i, row in enumerate(data[:3]):
                    logger.info(f"Row {i}: {row}")
            except Exception as e:
                logger.error(f"Error in unpack_slk: {str(e)}", exc_info=True)
                raise ValueError(f"Error parsing SLK file: {str(e)}")
            
            if not data:
                raise ValueError("No data found in file")
                
            # Define the expected columns and their display names
            expected_columns = {
                'STATION': 'Extension',
                'CO': 'Trunk',
                'TIME': 'Duration',
                'START': 'Call Time',
                'DIRECTION': 'Type',
                'CLI': 'Number',
                'COST': 'Cost',         # Make sure this matches exactly
                'ACCOUNT': 'Account Code'  # Make sure this matches exactly
            }
            
            try:
                # Extract headers from first row and clean them
                raw_headers = [str(h).strip().upper() for h in data[0] if str(h).strip()]
                logger.info(f"Raw headers from file: {raw_headers}")
                
                # Map raw headers to expected columns
                header_mapping = {}
                used_display_names = set()  # Track which display names have been used
                
                for i, raw_header in enumerate(raw_headers):
                    matched = False
                    # Try exact match first
                    if raw_header in expected_columns:
                        display_name = expected_columns[raw_header]
                        if display_name not in used_display_names:
                            header_mapping[i] = display_name
                            used_display_names.add(display_name)
                            matched = True
                            logger.info(f"Exact match - Header {i}: {raw_header} -> {display_name}")
                            continue
                    
                    # Try partial match if exact match failed
                    for exp_key, exp_value in expected_columns.items():
                        if (exp_key in raw_header or raw_header in exp_key) and exp_value not in used_display_names:
                            header_mapping[i] = exp_value
                            used_display_names.add(exp_value)
                            matched = True
                            logger.info(f"Partial match - Header {i}: {raw_header} -> {exp_value}")
                            break
                            
                    if not matched:
                        header_mapping[i] = raw_header.title()
                        logger.info(f"No match - Header {i}: {raw_header} -> {raw_header.title()}")
                
                logger.info(f"Final header mapping: {header_mapping}")
                
                # Create DataFrame with actual data rows (skip header row)
                df = pd.DataFrame(data[1:])
                
                # Filter out rows that contain header-like content
                df = df[~df.apply(lambda row: all(
                    str(val).strip().upper() in [h.upper() for h in expected_columns.keys()]
                    for val in row if str(val).strip()
                ), axis=1)]
                
                # Rename columns using the mapping
                df.columns = [header_mapping.get(i, f'Column {i+1}') 
                            for i in range(len(df.columns))]
                
                logger.info(f"DataFrame columns after mapping: {df.columns.tolist()}")
                
                # Store both headers and data separately in processed_data
                self.processed_data = {
                    'headers': df.columns.tolist(),
                    'data': df.values.tolist()
                }
                
            except Exception as e:
                logger.error(f"Error creating DataFrame: {str(e)}", exc_info=True)
                raise ValueError(f"Error creating DataFrame: {str(e)}")
            
            # Update report status
            self.processed_at = timezone.now()
            self.status = 'completed'
            self.is_processed = True
            self.total_records = len(df)
            self.processed_records = len(df)
            self.save()
            
            logger.info(f"Successfully processed file: {self.file_name}")
            
        except Exception as e:
            logger.error(f"Error processing file {self.file_name}: {str(e)}", exc_info=True)
            self.status = 'error'
            self.error_message = str(e)
            self.is_processed = False
            self.save()
            raise

    def unpack_slk(self):
        """
        Unpacks an SLK file and returns a list of lists containing the data.
        The first row contains headers, and subsequent rows contain the data.
        """
        if not self.file:
            raise ValueError("No file attached to this report")

        try:
            logger.info(f"Starting to process file: {self.file_name}")
            
            # Check if file is gzipped
            is_gzipped = self.file_name.endswith('.gz')
            logger.info(f"File is {'gzipped' if is_gzipped else 'not compressed'}")
            
            # Read the file content
            try:
                if is_gzipped:
                    logger.info("Decompressing gzipped file...")
                    with gzip.open(self.file.path, 'rt', encoding='utf-8') as f:
                        content = f.readlines()
                    logger.info("Successfully decompressed file")
                else:
                    logger.info("Reading uncompressed file...")
                    with open(self.file.path, 'r', encoding='utf-8') as f:
                        content = f.readlines()
                    logger.info("Successfully read file")
            except UnicodeDecodeError:
                # Try alternative encodings if UTF-8 fails
                encodings = ['latin1', 'cp1252', 'iso-8859-1']
                content = None
                for encoding in encodings:
                    try:
                        if is_gzipped:
                            with gzip.open(self.file.path, 'rt', encoding=encoding) as f:
                                content = f.readlines()
                        else:
                            with open(self.file.path, 'r', encoding=encoding) as f:
                                content = f.readlines()
                        logger.info(f"Successfully read file with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise ValueError("Could not decode file with any supported encoding")

            # Initialize data structures for SLK parsing
            data = {}  # Dictionary to store cell values: {y: {x: value}}
            max_x = 0  # Maximum column number
            max_y = 0  # Maximum row number
            
            # First pass: collect all cell values
            for line in content:
                line = line.strip()
                if not line or not line.startswith('C;'):
                    continue
                
                parts = line.split(';')
                if len(parts) < 4:
                    continue
                
                try:
                    # Extract X and Y coordinates and value
                    x_part = parts[1]
                    y_part = parts[2]
                    value_part = parts[3]
                    
                    if not (x_part.startswith('X') and y_part.startswith('Y')):
                        continue
                        
                    x = int(x_part[1:])  # Remove 'X' and convert to int
                    y = int(y_part[1:])  # Remove 'Y' and convert to int
                    value = value_part.strip('"K').strip()
                    
                    # Update max coordinates
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    
                    # Store the value
                    if y not in data:
                        data[y] = {}
                    data[y][x] = value
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping malformed line: {line}, Error: {str(e)}")
                    continue
            
            # Convert dictionary structure to list of lists
            result = []
            for y in range(1, max_y + 1):
                if y in data:
                    row = []
                    for x in range(1, max_x + 1):
                        row.append(data[y].get(x, ''))
                    if any(cell.strip() for cell in row):  # Only include non-empty rows
                        result.append(row)
            
            logger.info(f"Successfully parsed {len(result)} rows with {max_x} columns")
            return result

        except Exception as e:
            logger.error(f"Error processing file {self.file_name}: {str(e)}", exc_info=True)
            raise ValueError(f"Error processing file: {str(e)}")

    def delete(self, *args, **kwargs):
        # Delete the actual file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                try:
                    os.remove(self.file.path)
                    logger.info(f"Successfully deleted file: {self.file.path}")
                except Exception as e:
                    logger.error(f"Error deleting file {self.file.path}: {str(e)}")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('IPECS Report')
        verbose_name_plural = _('IPECS Reports')
        ordering = ['-created_at']
