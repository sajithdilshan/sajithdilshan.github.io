---
layout: post
title: "AJAX with ruby on rails"
date: 2013-08-21 17:28
comments: true
categories: [ruby on rails, AJAX, ruby]
---

As for the Software Engineering Project module in this semester I'm building a feed reader(similar to Google reader) using ruby on rails. And for this project I've been using AJAX heavily and Below is a simple tutorial to use AJAX with RoR. 

So here's the scenario. A list of feed subscriptions is displayed and when a user clicks on a item in that list, AJAX request is sent to the server to fetch the feed items(posts) of that feed and it is displayed inside the DIV tag with the id "feedlistcontainer". Let's assume the corresponding modelname is userfeed.rb and the controller is userfeeds_controller.rb

{% codeblock app/views/userfeeds/index.html.haml lang:haml %}
%div.row
  %div.col-md-9.col-md-push-3
    %div{"id" => "feedlistcontainer"}
       = render partial: "_feedlist"
  %div.col-md-3.col-md-pull-9
    %div.row
      %p Your Subscriptions
      %div.list-group
      - if @feeditems.nil?
        %p No subscriptions available
      - else
        - @feeditems.each_with_index do |feeditem,index|
          / %span.badge 14
          = link_to feeditem.feed_name, show_feed_list_path(:feed_id => feeditem.id), :class =>"list-group-item", remote: true
{% endcodeblock %}

{% codeblock app/views/userfeeds/_feedlist.html.haml lang:haml %}
%div.panel-group{"id" => "accordion"}
  - if @feeditem_list.nil?
    %p no item here
  - else
    - @feeditem_list.each_with_index do |feeditem, index|
      - $item_id = feeditem.id
      %div.panel{"id" => "panel#{$item_id}"}
        %div.panel-heading
          %h4.panel-title
            %a.accordion-toggle{"data-toggle" => "collapse", "data-parent" => "#accordion", "href" => "#feed#{$item_id}"}
              = feeditem.post_title
        %div.panel-collapse.collapse{"id" => "feed#{$item_id}"}
          %div.panel-body
              %p= feeditem.post_body.html_safe
{% endcodeblock %}

Keep in mind that I've used bootstrap 3 with the project, hence different class names for DIV tags. So above index.html.haml renders feed list inside "div.col-md-3.col-md-pull-9" tag. The userfeeds_controller initializes the @feeditems variable with an iteratable object of "feeds" which was returned to it by a model. Then it iterates over that object and for each entry it creates a link with remote link. Notify the "remote: true" syntax. That is the syntax which specifies that this is not a regular link, but it is an AJAX call. By clicking on that link, it will generate a GET remote rquest to show_feed_list_path and it will populate param hash with ":feed_id => feeditem.id" value. We have to add below code in the routes.rb file defining the show_feed_list_path

{% codeblock routes.rb lang:ruby %}
get "show_feed_list", to: "userfeeds#show_feed_list"
{% endcodeblock %}

And also feed items are rendered inside "div{"id" => "feedlistcontainer"}" tag. I've used an accordion to diplay the post list(feed items). The @feeditem_list will be initialized by the userfeeds_controller after the AJAX call.

Below is the userfeed_controller code corresponding to the above view template

{% codeblock app/controllers/userfeeds_controller.rb lang:ruby %}

  def index
    @feeditems = Userfeed.getUserFeedList(currentuser.userid)
  end

  def show_feed_list
    feed_id = params[:feed_id]
    @feeditem_list = Userfeed.get_feed_list(feed_id)

    respond_to do |format|
      format.js   # show_feed_list.js.haml
    end
  end

{% endcodeblock %}

What this code does is in the index method it initialized the @feeditems variable with an iteratable object which contains a list of feed subscriptions of a particular user."Userfeed.getUserFeedList(currentuser.userid)" method call can be different depending on how the Models are defined in the application. But the general ide is that @feeditems variable is initialized with a feed list somehow.

The After the ajax call show_feed_list method gets called. We extract the ID of the feed from param hash and using that we initialize @feeditem_list variable with an iteratable object of posts(feed items) in that particular feed. Again "Userfeed.get_feed_list(feed_id)" can be different. All we have to do is somehow initialize the @feeditem_list with corresponding post list.

Then it will pass this @feeditem_list to a file name "show_feed_list.js.haml". Remember RoR uses convention over configuration. So that's why it is passing the @feeditem_list to a javascript file with the same name of the method "show_feed_list".

{% codeblock app/views/userfeeds/show_feed_list.js.haml lang:haml %}
$('#feedlistcontainer').html("#{j(render("feedlist", :feeditem_list => @feeditem_list))}")
{% endcodeblock %}

Above is the content of the java script file. It will render the _feedlist.html.haml inside the DIV tag with id "feedlistcontainer" and pass the @feeditem_list variable from controller to the _feedlist.html.haml template. And that's it. We don't need extensive knowledge on java script or JQuery at all.