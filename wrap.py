import os
import io
from itertools import cycle
import zipfile
import argparse
import base64

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            print(file)
            source_file = os.path.join(root, file)
            zip_file = os.path.relpath(source_file, path)
            ziph.write(source_file, zip_file)

def encrypt_decrypt(input_data, key, cipher='xor'):
    if cipher == 'xor':
        key = [ord(c) for c in key]
        key_len = len(key)
        return bytes([b ^ key[i % key_len] for i, b in enumerate(input_data)])

def parse_args():
    parser = argparse.ArgumentParser(description="Wrap python module or URL")

    # Define the positional arguments
    parser.add_argument("location", choices=['local', 'remote'], help="location of the module or URL: local or remote")
    parser.add_argument("source", help="name of the module or remote URL")
    parser.add_argument("key", help="encryption key")

    # Define optional argument
    parser.add_argument("-o", "--output", help="output file path (only for local)")
    parser.add_argument("-a", "--arguments", help="arguments to the script")

    args = parser.parse_args()

    # Check if location is local but output file is not specified
    if args.location == 'local' and args.output is None:
        parser.error("the following arguments are required: -o/--output")

    return args
    
def main():
    args = parse_args()

    if args.location == 'local':
        local_directory =  os.path.normpath(os.path.realpath(os.path.dirname(__file__)))
        module_directory = os.path.join(local_directory,'modules', args.source)

        # Creating zip in memory
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(module_directory, zipf)
        
        data = zip_io.getvalue()
        encrypted_data = encrypt_decrypt(data, args.key)

        # Writing encrypted data to file
        with open(args.output, 'wb') as f:
            f.write(encrypted_data)
        
        mummy_path =  os.path.join(local_directory,'mummy.py')
        with open(mummy_path) as f:
            mummy_contents = f.read()
        
        mummy_contents += '\n\nimport shlex\n'
        mummy_contents += f'arguments_cmd = "{args.source} {args.arguments}"\n'
        mummy_contents += "module_args = shlex.split(arguments_cmd)\n"
        mummy_contents += f"run_module_locally('{args.output}', key='{args.key}', module_args=module_args)"

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.writestr('file.py', mummy_contents)

        memory_file.seek(0)
        base64_encoded = base64.b64encode(memory_file.read()).decode()
        print (f"\nCopy the {args.output} file to the remote host and run the code from the python interpreter:\n\n")
        print (f"import base64, io, zipfile; exec(io.TextIOWrapper(zipfile.ZipFile(io.BytesIO(base64.b64decode('{base64_encoded}'))).open('file.py')).read())")

if __name__ == '__main__':
    main()