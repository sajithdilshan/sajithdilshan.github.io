---
layout: post
title: "IntelliJ IDEA plugin for UltraESB"
date: 2014-02-14 19:04
comments: true
categories: [IntelliJ Idea, Plugin Development, UltraESB]
---

Recently I've developed an IntelliJ IDEA plugin for [UltraESB](http://www.adroitlogic.org/products/ultraesb.html) with few features and while doing that I've learned so much about the plugin development for IDEA. And also if you're an ultraesb developer, by installing this plugin you'll be able to enjoy below mentioned features.

### Creating multi module projects and deployment units
{% img http://docs.adroitlogic.org/download/attachments/11174355/unita-2.png "New Deployment Unit Wizard" %}

You can create new Multi-Module projects and new Deployment UNits straight from the new project/module wizard respectively. All you have to do is fill out the necessary fields and IDEA will do the rest for you.

### File templates, Live templates, Language injection and Code generation
{% img http://docs.adroitlogic.org/download/attachments/11174358/inject.png "Java language injection" %}
 
This plugin contains new sequence file template, few live templates, Java language injection for XML tags and code generation facility. You can simply read the [full documentationn](http://docs.adroitlogic.org/display/esb/IntelliJ+IDEA+Plugin) of the plugin to know more.

I'm planning to write a series of tutorials explaining how I implemented each and every feature. The plugin is open source and the source code is available here. You can download the plugin straight from Jetbrain's [plugin repositoryy](http://plugins.jetbrains.com/plugin/7396)

In the future we're planing to integrate [Spring Open API](http://confluence.jetbrains.com/display/IDEADEV/Spring+API+Guide) into the plugin so that we can provide navigation and refactoring facilities for the proxy, endpoint and sequence beans.

And last but not least I'd like to thank IntelliJ IDEA [Open API and Plugin Development communityy](http://devnet.jetbrains.com/community/idea/open_api_and_plugin_development) especially [Alexander Doroshko](http://devnet.jetbrains.com/people/AlexanderD) and [Yann Cebron](http://devnet.jetbrains.com/people/yannc76) for providing immense support.
