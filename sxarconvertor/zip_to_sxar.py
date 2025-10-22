import sys
import zipfile
import os
import struct

def create_sxar_from_zip(zip_path):
    """
    Converts a .zip archive to a .sxar archive.

    The .sxar format is based on the provided Lua script:
    - 4-byte magic number: 'SXAR'
    - 4-byte unsigned int (little-endian): Total number of files.
    - 4-byte unsigned int (little-endian): Header start offset (always 16).
    - 4-byte unsigned int (little-endian): Data block start offset.
    - File Metadata Blocks:
        - 1-byte unsigned int: Length of the file name.
        - N-bytes: The file name (UTF-8 encoded).
        - 4-byte unsigned int (little-endian): Offset of the file data from the start of the data block.
        - 4-byte unsigned int (little-endian): Size of the file data in bytes.
    - Data Block:
        - Concatenated raw data of all files.
    """
    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        print(f"Error: The provided file is not a valid .zip file: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_infos = [info for info in zf.infolist() if not info.is_dir()]
            
            if not file_infos:
                print("Error: The zip file is empty.")
                return

            print(f"Found {len(file_infos)} files to process in {os.path.basename(zip_path)}.")

            metadata_size = 0
            file_metadata = []
            
            # First pass: gather file info and calculate metadata size
            current_data_offset = 0
            for info in file_infos:
                file_name_bytes = info.filename.encode('utf-8')
                file_size = info.file_size

                # Metadata size for this file: 1 (name length) + len(name) + 4 (offset) + 4 (size)
                metadata_size += 1 + len(file_name_bytes) + 8
                
                file_metadata.append({
                    "name_bytes": file_name_bytes,
                    "offset": current_data_offset,
                    "size": file_size,
                    "zip_info": info
                })
                current_data_offset += file_size


            # --- Header Information ---
            magic_number = b'SXAR'
            total_files = len(file_infos)
            header_start = 16  # The size of the initial header part
            data_start = header_start + metadata_size

            # --- Write the .sxar file ---
            output_filename = os.path.splitext(zip_path)[0] + '.sxar'
            print(f"Creating archive: {output_filename}")

            with open(output_filename, 'wb') as sxar_file:
                # Write the main header (16 bytes)
                # '<' denotes little-endian, 'I' is a 4-byte unsigned integer
                sxar_file.write(magic_number)
                sxar_file.write(struct.pack('<I', total_files))
                sxar_file.write(struct.pack('<I', header_start))
                sxar_file.write(struct.pack('<I', data_start))

                # Write the file metadata section
                for meta in file_metadata:
                    name_bytes = meta["name_bytes"]
                    name_len = len(name_bytes)
                    
                    # '<' denotes little-endian, 'B' is a 1-byte unsigned integer
                    sxar_file.write(struct.pack('<B', name_len))
                    sxar_file.write(name_bytes)
                    sxar_file.write(struct.pack('<I', meta["offset"]))
                    sxar_file.write(struct.pack('<I', meta["size"]))
                
                # Write the main data block
                for meta in file_metadata:
                    with zf.open(meta["zip_info"]) as source_file:
                        sxar_file.write(source_file.read())
            
            print("Conversion successful!")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        zip_file_path = sys.argv[1]
        create_sxar_from_zip(zip_file_path)
    else:
        print("Usage: Drag and drop a .zip file onto the convert.bat file.")
        print("Or run from command line: python zip_to_sxar.py <path_to_zip_file>")