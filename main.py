import os
import glob
import argparse
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


# 加密方式: 对每位字节进行异或计算
# 异或 XOR: 二进制计算, 相同位得 0, 不同位得 1
# a XOR b = c, a XOR c = b


# get the img format and the password: XOR value
def decrypt(byte_data):
    img_type = {
        'jpg': (0xff, 0xd8),
        'png': (0x89, 0x50),
        'gif': (0x47, 0x49)
    }
    for key, value in img_type.items():
        if byte_data[0] ^ value[0] == byte_data[1] ^ value[1]:
            return key, byte_data[0] ^ value[0]
    
    return None, None


# convert .dat to image
def dat_to_img(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as file:
        byte_data = file.read()
        img_format, password = decrypt(byte_data[:2])

        if not img_format:
            return False, None
        
        new_data = bytes([b ^ password for b in byte_data])
        output_file_path = output_file_path + f".{img_format}"

        with open(output_file_path, 'wb') as output_file:
            output_file.write(new_data)
    return True, output_file_path


# determine the output file name based on the input file
# {output_path}/wxid_/Image/chat_id/{date}/{image}
def get_output_name(file_path, output_path):
    if '\\' in file_path:
        parts = file_path.split('\\')
    else:
        parts = file_path.split('/')
        
    return os.path.join(output_path, parts[-7], parts[-3], parts[-4], parts[-2], parts[-1].split('.')[0])


# create output_path and convert
def convert_process(file_path, output_path):
    output_file_path = get_output_name(file_path, output_path)
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    return dat_to_img(file_path, output_file_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert wechat .dat to image.')
    parser.add_argument('-i', '--input', type=str, required=True, help='one .dat file or dir')
    parser.add_argument('-o', '--output', type=str, default='image', help='the output folder to save as (default: image)')
    parser.add_argument('-n', '--num', type=int, default=None, help='number of parallel workers (default: CPU count)')
    
    args = parser.parse_args()
    file_path = args.input
    output_path = args.output
    t0 = time.time()

    # single dat file
    if os.path.isfile(file_path):
        file_name = os.path.split(file_path)[1].split(".")[0]
        
        # create output_path
        if not os.path.isdir(output_path):
            os.mkdir(output_path)

        output_file_path = os.path.join(output_path, file_name)
        status, path = dat_to_img(file_path, output_file_path)
        if status:
            print(f"Success, converted to {path}")
        else:
            print(f"Unknown format: {file_path}")

    # wxid dir
    elif os.path.isdir(file_path):
        files = glob.glob(os.path.join(file_path, '**', '*.dat'), recursive=True)
        # files = glob.glob(os.path.join(file_path, '**', 'Image/*/*.dat'), root_dir=file_path, recursive=True)
        # files = glob.glob(os.path.join(file_path, '**', 'Thumb/*/*.dat'), root_dir=file_path, recursive=True)
        print(f"Found {len(files)} .dat files")
        
        with ProcessPoolExecutor(max_workers=args.num) as executor:
            futures = {executor.submit(convert_process, f, output_path): f for f in files}
            count = 0
            with tqdm(total=len(files), desc="Processing .dat files") as pbar:
                for future in as_completed(futures):
                    file = futures[future]
                    try:
                        status, _ = future.result()
                        if status:
                            count += 1
                        else:
                            print(f"\nUnknown format: {file}")
                    except Exception as e:
                        print(f"\nUnexpected error processing {file}: {str(e)}")
                    finally:
                        pbar.update(1)
        if count == len(files):
            print(f"All success, cost {time.time() - t0:.2f}s")
        else:
            print(f"{count} success, cost {time.time() - t0:.2f}s")

    else:
        print(f"Please enter the correct file path or directory")


    








            
    
