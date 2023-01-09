// npm install md5 -g
let md5 = require("md5");
let Array = [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 10, 11, 12, 13, 14, 15];
let character = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe=";// 固定

function md5_str_to_array(a) {
    let array = [];
    for (let idx = 0; idx < a.length;) {
        array.push(Array[a.charCodeAt(idx++)] << 4 | Array[a.charCodeAt(idx++)])
    }
    return array;
}

function md5_encrypt(url_path) {
    return md5_str_to_array(md5(md5_str_to_array(md5(url_path))));
}

function encoding_conversion(a, b, c, e, d, t, f, r, n, o, i, _, x, u, s, l, v, h, p) {
    let y = new Uint8Array(19);
    y[0] = a, y[1] = i, y[2] = b, y[3] = _, y[4] = c, y[5] = x, y[6] = e, y[7] = u,
        y[8] = d, y[9] = s, y[10] = t, y[11] = l, y[12] = f, y[13] = v, y[14] = r, y[15] = h, y[16] = n, y[17] = p, y[18] = o;
    return String.fromCharCode.apply(null, y);
}

function encoding_conversion2(a, b) {
    let c, e = [], d = 0, t = "", r = 0, o = 0, n = 0;
    for (let f = 0; f < 256; f++) {
        e[f] = f;
    }
    for (; r < 256; r++) {
        d = (d + e[r] + a.charCodeAt(r % a.length)) % 256, c = e[r], e[r] = e[d], e[d] = c;
    }
    d = 0;
    for (; o < b.length; o++) {
        d = (d + e[n = (n + 1) % 256]) % 256, c = e[n], e[n] = e[d], e[d] = c, t += String.fromCharCode(b.charCodeAt(o) ^ e[(e[n] + e[d]) % 256]);
    }
    return t;
}

function encoding_conversion3(a, b, c) {
    return String.fromCharCode(a) + String.fromCharCode(b) + c;
}

function calculation(a1, a2, a3) {
    let x1 = (a1 & 255) << 16;
    let x2 = (a2 & 255) << 8;
    let x3 = x1 | x2 | a3;
    return character[(x3 & 16515072) >> 18] + character[(x3 & 258048) >> 12] + character[(x3 & 4032) >> 6] + character[x3 & 63];
}

function getXBoGust(url_path) {
    // 不知道什么东西先固定
    let array1 = md5_str_to_array(md5("d4+pTKoNjJFb5tMtAC3XB9XrDDxlig1kjbh32u+x5YcwWb/me2pvLTh6ZdBVN5skEeIaOYNixbnFK6wyJdl/Lcy9CDAcpXLLQc3QFKIDQ3KkQYie3n258eLS1YFUqFLDjn7dqCRp1jjoORamU2SV"));
    let array2 = md5_str_to_array(md5(md5_str_to_array("d41d8cd98f00b204e9800998ecf8427e")));
    // timer 1672337078.109 可得 DFSzswVuDlhANxXhSkLw9l9WX7rw
    let url_path_array = md5_encrypt(url_path), timer = new Date().getTime() / 1000, ct = 536919696, array3 = [], array4 = [], str = "";
    let new_array = [
        64, 0.00390625, 1, 8, // 固定写死
        url_path_array[14], url_path_array[15], array2[14], array2[15], array1[14], array1[15],
        timer >> 24 & 255, timer >> 16 & 255, timer >> 8 & 255, timer >> 0 & 255,
        ct >> 24 & 255, ct >> 16 & 255, ct >> 8 & 255, ct >> 0 & 255 // 可以固定写死
    ];
    new_array.push(new_array.reduce(function (a, b) {
        return a ^ b;
    }));

    for (let idx = 0; idx < new_array.length; idx += 2) {
        array3.push(new_array[idx])
        array4.push(new_array[idx + 1])
    }
    let garbled_code = encoding_conversion3.apply(null, [2, 255, encoding_conversion2.apply(null,
        ["ÿ", encoding_conversion.apply(null, array3.concat(array4).slice(0, 19))]
    )]);

    for (let idx = 0; idx < garbled_code.length;)
        str += calculation(garbled_code.charCodeAt(idx++), garbled_code.charCodeAt(idx++), garbled_code.charCodeAt(idx++))
    return str;
}

// let xxx = "device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7166234565919477005&cursor=0&count=20&item_type=0&insert_ids=&rcFT=&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=104.0.0.0&browser_online=true&engine_name=Blink&engine_version=104.0.0.0&os_name=Windows&os_version=10&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7182571494127535616&msToken=BAsHVO5ryQtHyUqtVIOpdhHNHTr4LpedaPHBWiERWgaPcuCNnhIUR1JzxW3ND6-0nQ7bfXM6gzZ_XNzxQHKFtdN3bRYBwZtYkSZ-76bSvYPnxyOk8okq"
// console.log(getXBoGust(xxx));