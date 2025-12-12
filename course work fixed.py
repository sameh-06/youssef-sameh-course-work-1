delimiter = "..."


## read message from file ##
def read_message_from_file(file_location):
    folder = open(file_location, "r", encoding="utf-8")
    information = folder.read()
    folder.close()
    return information

## get image bytes ##
def read_binary_file(image_location):
    folder = open(image_location, "rb")
    information = folder.read()
    folder.close()
    return information

## binary file ##
def write_binary_file(image_location, information):
    folder = open(image_location, "wb")
    folder.write(information)
    folder.close()

## text to bytes ##
def text_to_bytes(text):
    return list(text.encode("utf-8"))

## bytes to text ##
def bytes_to_text(byte):
    return bytes(byte).decode("utf-8", errors = "ignore")

## bytes to bits ##
def bytes_to_bits(byte):
    bits = []
    for i in byte:
        for g in range(7, -1, -1):
            bits.append((i >> g) & 1)
    return bits

## bits to bytes ##
def bits_to_bytes(bits):
    if len(bits) % 8 != 0:
        raise ValueError("number of bits is not a multiple of 8")
    output = []
    for i in range(0, len(bits), 8):
        byte = 0
        for g in range(8):
            byte = (byte << 1) | (bits[i + g] & 1) 
        output.append(byte)
    return output


## data offset ##
def find_pixel_data_offset(image_bytes):
    do0 = image_bytes[10]
    do1 = image_bytes[11]
    do2 = image_bytes[12]
    do3 = image_bytes[13]
    
    return do0 + (do1 << 8) + (do2 << 16) + (do3 << 24)

## get least significant bit ##
def get_least_significant_bit(byte):
    return (byte & 1)

## set least significant bit ##
def set_least_significant_bit(byte, bit):
    return (byte & 0b11111110) | (bit & 1)


def first():
    while True:
        print("a. Encode message")
        print("b. Decode message")
        print("c. Exit")
        your_choice = input("what do you want to do: ")
        if your_choice == "a":
            encode()                
        elif your_choice == "b":
            decode()
        elif your_choice == "c":
            break
        else:
            print("choose an existiing option")


def encode():
    image_location = input("enter the image location: ")
    finished_image_location = input("enter where the finished image should be saved: ")
    if not finished_image_location.lower().endswith(".bmp"):
        finished_image_location += "decoded.bmp"
    print("1. type your secret")
    print("2. read message from a file")
    choice = input("what are you going to do: ")
    if choice == "1":
        secret_message = input("enter your secret message: ")
    elif choice == "2":
        file_location = input("enter the file location: ")
        secret_message = read_message_from_file(file_location)
    else:
        print("invalid option")
        return
    message_bytes = text_to_bytes(secret_message)
    delimiter_bytes = text_to_bytes(delimiter)
    payload_bytes = message_bytes + delimiter_bytes
    payload_bits = bytes_to_bits(payload_bytes)
    image_bytes = read_binary_file(image_location)
    dataOffset = find_pixel_data_offset(image_bytes)

    available = len(image_bytes) - dataOffset
    needed = len(payload_bits)
    if needed > available:
        print("your message is too long to be encoded in this image")
        return
    output = bytearray(image_bytes)
    x = 0
    for i in range(dataOffset, len(output)):
        if x >= needed:
           break
        else:
            output[i] = set_least_significant_bit(output[i], payload_bits[x])
            x += 1
    write_binary_file(finished_image_location, output)
    print(f"your message has been encoded and saved to {finished_image_location}")


def decode():
    print("decoding the hidden message from the image...")
    secret_message = input("enter the location of the image containing your hidden message: ")
    picture_bytes = read_binary_file(secret_message)
    dataOffset = find_pixel_data_offset(picture_bytes)
    delimiter_bits = bytes_to_bits(text_to_bytes(delimiter))
    delim_length = len(delimiter_bits)
    concated_bits = []
    for i in range(dataOffset, len(picture_bytes)):
        glsb = get_least_significant_bit(picture_bytes[i])
        concated_bits.append(glsb)
        if len(concated_bits) >= delim_length:
            if concated_bits[-delim_length:] == delimiter_bits:
                hidden_message_bits = concated_bits[:-delim_length]
                hidden_message_bytes = bits_to_bytes(hidden_message_bits)
                result = bytes_to_text(hidden_message_bytes)
                print(f"after analyzing, the hidden message sent to you is : {result} ")
                return
    print("delimeter not found, no hidden message detected")


first()