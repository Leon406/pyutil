from server.OcrServer import post_process

if __name__ == '__main__':
    test_data = ["一nw2ac", "dasd-f", "=nw2ac", ">4cn5x", "4cn5x>", "<nw2ac", "-mndm2", ")amxdx", "/f2ax7", "十ycb4p",
                 "你b好a"]
    for d in test_data:
        print(post_process(d))
