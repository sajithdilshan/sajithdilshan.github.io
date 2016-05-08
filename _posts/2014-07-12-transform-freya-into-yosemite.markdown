---
layout: post
title: "Transform Freya into Yosemite"
date: 2014-07-12 14:33:24 +0530
comments: true
categories: [elementary os, freya, os x yosemite, xgtk theme]
---

This post is about transforming Elementary OS Freya into OS X Yosemite (only the appearance ;-) ). If you're on eOS Freya, type the below command into the terminal

{% codeblock %}
sudo add-apt-repository ppa:gnome3-team/gnome3 && sudo add-apt-repository ppa:gnome3-team/gnome3-staging && sudo add-apt-repository ppa:ricotz/testing && sudo add-apt-repository ppa:elementary-os/daily && sudo apt-get update && sudo apt-get dist-upgrade -y
{% endcodeblock %}

Above command will add the latest gnome and elmentary daily PPAs to your system and perform a distribution upgrade. After that type below command in-order to install nautilus and epiphany.

{% codeblock %}
sudo apt-get install epiphany-browser nautilus
{% endcodeblock %}

Now you can download the XGtk theme from this [link](http://kxmylo.deviantart.com/art/Xgtk-theme-465195148) and place the theme folder within /usr/share/theme and apply xGtk using elementary-tweak. Now reboot your pc and if everything goes well, your desktop will look as below.

{% img https://lh5.googleusercontent.com/-CU3VR-Vsimw/U8DcA_wTsdI/AAAAAAAABgM/UR5Rke_Ym5k/w1010-h568-no/screnn.png %}

A huge thank goes to [Camilo Higuita](https://plus.google.com/u/0/104908072417273204416/about) for creating this wonderful theme and for providing the instructions.