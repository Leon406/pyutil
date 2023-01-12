// npm install md5 -g
let md5 = require("md5");
let Array = [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 10, 11, 12, 13, 14, 15];
let character = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=";// 固定

function hex_to_bytearray(a) {
    let array = [];
    for (let idx = 0; idx < a.length;) {
        array.push(Array[a.charCodeAt(idx++)] << 4 | Array[a.charCodeAt(idx++)])
    }
    return array;
}

function md5_encrypt(url_path) {
    return hex_to_bytearray(md5(hex_to_bytearray(md5(url_path))));
}

function conversion(array) {
    return String.fromCharCode.apply(null, array);
}

function encoding_conversion2(a, b) {
    let c, e = [], d = 0, t = "";
    for (let f = 0; f < 256; f++) {
        e[f] = f;
    }
    for (let r = 0; r < 256; r++) {
        d = (d + e[r] + a.charCodeAt(r % a.length)) % 256,
            c = e[r],
            e[r] = e[d],
            e[d] = c;
    }

    d = 0;
    for (let o = 0,n = 0; o < b.length; o++) {
        d = (d + e[n = (n + 1) % 256]) % 256,
            c = e[n],
            e[n] = e[d],
            e[d] = c,
            t += String.fromCharCode(b.charCodeAt(o) ^ e[(e[n] + e[d]) % 256]);
    }
    return t;
}

function calculation(a1, a2, a3) {
    let x1 = (a1 & 255) << 16;
    let x2 = (a2 & 255) << 8;
    let x3 = x1 | x2 | a3;
    return character[(x3 & 16515072) >> 18] + character[(x3 & 258048) >> 12] + character[(x3 & 4032) >> 6] + character[x3 & 63];
}

function getXBoGust(url_path) {
    let array1 = [216, 130, 1, 201, 52, 71, 7, 172, 222, 114, 97, 177, 88, 101, 108, 14];
    let array2 = [89, 173, 178, 78, 243, 205, 190, 2, 151, 240, 91, 57, 88, 39, 69, 63];
    let url_path_array = md5_encrypt(url_path), str = "";
    let new_array = [
        0, 0, 1, 8, // 固定写死
        url_path_array[14], url_path_array[15], array2[14], array2[15], array1[14], array1[15],
       0, 0, 0, 0, // 可以固定写死
       0, 0, 0, 0 // 可以固定写死
    ];
    new_array.push(new_array.reduce(function (a, b) {
        return a ^ b;
    }));

    let garbled_code = "\x02\xff" + encoding_conversion2("ÿ", conversion(new_array));

    for (let idx = 0; idx < garbled_code.length;)
        str += calculation(garbled_code.charCodeAt(idx++), garbled_code.charCodeAt(idx++), garbled_code.charCodeAt(idx++))
    return str;
}

// let xxx = "device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7166234565919477005&cursor=0&count=20&item_type=0&insert_ids=&rcFT=&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=104.0.0.0&browser_online=true&engine_name=Blink&engine_version=104.0.0.0&os_name=Windows&os_version=10&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7182571494127535616&msToken=BAsHVO5ryQtHyUqtVIOpdhHNHTr4LpedaPHBWiERWgaPcuCNnhIUR1JzxW3ND6-0nQ7bfXM6gzZ_XNzxQHKFtdN3bRYBwZtYkSZ-76bSvYPnxyOk8okq"
// console.log(getXBoGust(xxx));