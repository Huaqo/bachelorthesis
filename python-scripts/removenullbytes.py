import sys


def clean_file(input_path):
    try:
        output_path = input_path.replace('.', '_clean.')
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as file:
            file_content = file.read()

        clean_content = file_content.replace('\x00', '')

        with open(output_path, 'w', encoding='utf-8') as clean_file:
            clean_file.write(clean_content)
        print('Null bytes removed from file:', input_path)
    except Exception as e:
        print(f'Error processing file {input_path}: {e}')
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python removenullbytes.py <file_path>')
        sys.exit(1)
    else:
        input_path = sys.argv[1]
        clean_file(input_path)
