---
layout: post
title: "Introducing UltraStudio"
date: 2017-01-12T12:44:04+05:30
comments: true
categories: [UltraStudio, Project-X, UltraESB-X, IntelliJIDEA]
---

For the past couple of months, we at AdroitLogic have been quite busy developing our brand new product stack. Now, after months of tiresome efforts, we are excited to present to you **UltraStudio**, the new Graphical Integration Development Environment we have built to make the UltraESB-X project developer’s life easier.

UltraStudio is a fully featured integration flow development environment for UltraESB-X. It is built on top of the world’s best IDE, IntelliJ IDEA, so you could have the best of both worlds. If you are already using IntelliJ IDEA, you can integrate UltraStudio into your IDE with just a few clicks.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/ultrastudio.png %}

With UltraStudio, developing a mediation sequence—or **integration flow**, as we call it now—is just a matter of playing around with building blocks—**connectors** and **processors**. Want to expose a HTTP endpoint? Just drag-and-drop a HTTP ingress connector from the palette and configure it. Want to convert the inbound XML message to JSON? Add an XML-to-JSON transformer and attach it to the connector. With the super-simple graphical UI, a complex flow that takes hours of design and hundreds of lines of code could come to life within a matter of minutes.

UltraStudio comes with hundreds of resources to kickstart your integration project, including a lot of sample projects to help you understand the new development flow. With a wide range of connectors for JMS, HTTP, FIX, AS2, SFTP, AMQP and other protocols, and processors to manipulate the messages flowing through the UltraESB-X, developing integration flows has become easier and more intuitive than ever.

Having said that, if you feel like writing your own processor or connector, you can simply go ahead and do it within your IDE itself since the underlying <a href="http://blog.ruwan.org/2017/01/the-x_10.html" target="_blank">Project-X</a> framework supports extensibility by nature. Further, you can run the flow you have created within the IDE, and trace the details of the message which went through each component to debug any possible issues in your flow as well.

Last but not the least, have a sneak peek at the following screencast on how to develop, run and test an integration project with the new UltraStudio by AdroitLogic!


<div class="videoWrapper">
<iframe width="760" height="430" src="https://www.youtube.com/embed/OSjfSwMv0Xo" frameborder="0" allowfullscreen></iframe>
</div>

