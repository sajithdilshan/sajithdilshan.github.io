---
layout: post
title: "The Woes of WebSockets"
date: 2014-03-26 12:49
comments: true
categories: 
---

Lately I've been developing a server side implementation of [Web Socket Protocol](https://tools.ietf.org/html/rfc6455) and I must say even though the core concept of Web Socket protocol is awesome, its framing specification has got it all wrong. Let's start with the definition of a Web Socket frame.

     0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-------+-+-------------+-------------------------------+
     |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
     |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
     |N|V|V|V|       |S|             |   (if payload len==126/127)   |
     | |1|2|3|       |K|             |                               |
     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
     |     Extended payload length continued, if payload len == 127  |
     + - - - - - - - - - - - - - - - +-------------------------------+
     |                               |Masking-key, if MASK set to 1  |
     +-------------------------------+-------------------------------+
     | Masking-key (continued)       |          Payload Data         |
     +-------------------------------- - - - - - - - - - - - - - - - +
     :                     Payload Data continued ...                :
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     |                     Payload Data continued ...                |
     +---------------------------------------------------------------+

As you can see above, it is a total mess. My biggest complain is about the masking of frame's payload when they are sent from a client to a server. The purpose of this masking is to prevent [cache poisoning in proxies](https://tools.ietf.org/html/rfc6455#page-51). But what does cache poisoning got to do with the Web Socket protocol? It is a vulnerability found on really old out-of-date proxies and why does Web Socket protocol has to pay the price for that? 

The real problem occurs when unmasking the frame's payload. You have to XOR the masked payload with the mask key and need I remind you that XORing is CPU intensive when you have to unmask thousands of frames per minute. Why don't we just let those old proxies suffer the cache poisoning (proxy users could either upgrade to a new version or the proxy vendor could release a patch for this particular vulnerability) and rid the Web Sockets from this misery of masking. 

The next problem is the payload length. 64 bits can be to specify the number of bytes in the payload. That means 2^64 = [18 quintillion](http://www.wolframalpha.com/input/?i=2%5E64), which is more bytes than the [number of stars in the Milky Way galaxy](http://www.wolframalpha.com/input/?i=number+of+stars+in+the+Milky+Way+galaxy). Is it really practical to use such a large payload? Apart from that, there is another feature of continuous frames to handle such scenario.

Let's use a fixed size of 4 bytes(size of an integer) to specify the payload length. If the payload is larger than that, one could use the continuous framing mechanism. Having a fixed number of bytes to represent the payload length is always better than a dynamic size.

After applying above improvements, I present you a more practical definition of a Web Socket frame as below. What do you think about it? 

     0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-------+-+-------------+-------------------------------+
     |F|R|R|R| opcode|         Payload length (Fixed Size)           |
     |I|S|S|S|  (4)  |                  (32)                         |
     |N|V|V|V|       |                                               |
     | |1|2|3|       |                                               |
     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
     |Payload length |          Payload Data                         |
     +-------------------------------- - - - - - - - - - - - - - - - +
     :                     Payload Data continued ...                :
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     |                     Payload Data continued ...                |
     +---------------------------------------------------------------+
