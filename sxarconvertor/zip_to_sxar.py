#!/usr/bin/env python3
"""
ZIP to SXAR Converter
Converts ZIP archives to SXAR (StarfallEx Archive) format
"""

import sys
import os
import struct
import zipfile
from pathlib import Path

class SXARWriter:
    """Writes SXAR archive files"""
    
    MAGIC = 0x52415853  # 'SXAR' in little-endian
    
    def __init__(self):
        self.files = []
        
    def add_file(self, name, data):
        """Add a file to the archive"""
        # Ensure forward slashes in paths
        name = name.replace('\\', '/')
        # Add leading slash if not present
        if not name.startswith('/'):
            name = '/' + name
        self.files.append((name, data))
    
    def write(self, output_path):
        """Write the SXAR archive to disk"""
        with open(output_path, 'wb') as f:
            # Calculate offsets
            header_size = 16  # Magic + file count + header start + data start
            
            # Calculate file info section size
            file_info_size = 0
            for name, data in self.files:
                file_info_size += 1  # name length byte
                file_info_size += len(name)  # name
                file_info_size += 4  # offset
                file_info_size += 4  # size
            
            header_start = 16
            data_start = header_start + file_info_size
            
            # Write header
            f.write(struct.pack('<I', self.MAGIC))  # Magic number
            f.write(struct.pack('<I', len(self.files)))  # Total files
            f.write(struct.pack('<I', header_start))  # Header start
            f.write(struct.pack('<I', data_start))  # Data start
            
            # Write file info and calculate data offsets
            current_data_offset = 0
            file_data_info = []
            
            for name, data in self.files:
                # Write name length and name
                name_bytes = name.encode('utf-8')
                f.write(struct.pack('B', len(name_bytes)))  # Name length (1 byte)
                f.write(name_bytes)  # Name
                
                # Write offset (relative to data start)
                f.write(struct.pack('<I', current_data_offset))
                
                # Write size
                f.write(struct.pack('<I', len(data)))
                
                # Store for later writing
                file_data_info.append(data)
                current_data_offset += len(data)
            
            # Write file data
            for data in file_data_info:
                f.write(data)

def convert_zip_to_sxar(zip_path, output_path=None):
    """Convert a ZIP file to SXAR format"""
    
    if not os.path.exists(zip_path):
        print(f"Error: File not found: {zip_path}")
        return False
    
    if not zipfile.is_zipfile(zip_path):
        print(f"Error: Not a valid ZIP file: {zip_path}")
        return False
    
    # Generate output path if not specified
    if output_path is None:
        output_path = Path(zip_path).with_suffix('.sxar')
    
    try:
        writer = SXARWriter()
        
        # Read ZIP and add files to SXAR
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            print(f"Converting {len(file_list)} files from ZIP to SXAR...")
            
            for file_name in file_list:
                # Skip directories
                if file_name.endswith('/'):
                    continue
                    
                # Read file data
                try:
                    data = zf.read(file_name)
                    writer.add_file(file_name, data)
                    print(f"  Added: {file_name} ({len(data)} bytes)")
                except Exception as e:
                    print(f"  Warning: Could not read {file_name}: {e}")
        
        # Write SXAR file
        writer.write(output_path)
        
        print(f"\nSuccess! SXAR archive created: {output_path}")
        print(f"Total files: {len(writer.files)}")
        print(f"Archive size: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

def main():
    """Main entry point"""
    
    print("ZIP to SXAR Converter")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python zip_to_sxar.py <input.zip> [output.sxar]")
        print("\nOr drag and drop a ZIP file onto the batch file.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_zip_to_sxar(input_path, output_path)
    
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)
    else:
        input("\nPress Enter to exit...")
        sys.exit(0)

if __name__ == "__main__":
    main()