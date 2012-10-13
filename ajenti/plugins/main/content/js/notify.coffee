class Notification
    constructor: (@text, @timeout, @notificator, @position) ->
        @dom = $("""
            <div class="notification">
                #{@text}
            </div>
        """)

        @active = true
        @position = 0
        @dom.css {top: @position + 'px', left: '300px'}
        @dom.animate {left: '0px'}, 500, 'swing'
        setTimeout @remove, @timeout

    remove: () =>
        @dom.animate {left: '300px'}, 500, 'swing', () =>
            @notificator.notifications.pop this
                
    moveUp: (dy) =>
        @position -= dy
        @dom.animate {top: @position + 'px'}, 500, 'swing'


class Notificator
    constructor: () ->
        @notifications = []

    notify: (text, timeout) ->
        timeout ?= 2000
        for notification in @notifications
            do (notification) =>
                notification.moveUp(50)
        notification = new Notification(text, timeout, this, 0)
        @notifications.push notification
        $('#notifications').append notification.dom


window.Notificator = new Notificator()