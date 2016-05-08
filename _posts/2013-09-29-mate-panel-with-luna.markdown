---
layout: post
title: "Mate panel with Luna"
date: 2013-09-29 04:47
comments: true
categories: [elementary os luna, mate panel, global menu]
---

So this tutorial is about how to install mate-panel in Elementary OS Luna. Let's just get started right away.

First we need to add the mate repository to our system. Keep in mind this is only for precise (Ubuntu 12.04) systems. Open a terminal and run below command.

{% codeblock %}
sudo add-apt-repository "deb http://packages.mate-desktop.org/repo/ubuntu/ precise main" && sudo apt-get update
{% endcodeblock %}

Now we need to install mate panel and its dependencies. And also the required indicator-applets. 

{% codeblock %}
sudo apt-get install mate-panel mate-core gtk2-engines-pixbuf mate-indicator-applet appmenu-gtk appmenu-gtk3 indicator-appmenu-gtk2 indicator-sound-gtk2 indicator-application-gtk2 indicator-datetime-gtk2 indicator-session-gtk2
{% endcodeblock %}

Now we are all set. We just have to replace wingpanel with mate panel. Inorder to do that open dconf-editor and navigate to org -> pantheon -> cerbere and in the "monitored-processes" section replace wingpanel with mate-panel like in the below image. After that logout and login again.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/1.png %}
<!-- more -->

After logging back you can see the mate-panel instead of wingpanel. Now we have to customize it a bit to make it look better. If you are familiar with gnome-panel, then customizing mate-panel is just as same as customizing gnome-panel. 

You can change the background of the panel by right clicking it and selecting properties. Then change the size to 22 px and go to the background tab and give [this](https://dl.dropboxusercontent.com/u/30358512/blog/panel-bg.png) image as the background image. 

Then in-order to add indicators, right click on the panel and select "Add to Panle". After that add "Indicator Applet Appmenu" and "Indicator Applet Complete" to your panel. You can create a "Custom Application Launcher" for slingshot if you like. And for best eye-candy, use [elementary-cupertino](https://dl.dropboxusercontent.com/u/30358512/elementary-cupertino.tar.gz) theme. Well that's it. Now your desktop should look similar to the below image.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/2.png %}





