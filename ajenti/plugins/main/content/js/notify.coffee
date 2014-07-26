class AjentiNotification
    constructor: (@type, @text, @timeout, @notificator, @position) ->
        @dom = jQuery("""
            <div class="notification #{@type}">
                #{@text}
            </div>
        """)

        @active = true
        @position = 0
        @dom.css {top: @position + 'px', left: '300px'}
        @dom.animate {left: '0px'}, 500, 'swing'
        setTimeout @remove, @timeout

    remove: () =>
        @dom.animate {left: '300px'}, 500, 'swing'
        setTimeout () =>
            @notificator.notifications.pop this
            @dom.remove()
        , 500

    moveUp: (dy) =>
        @position -= dy
        @dom.animate {top: @position + 'px'}, 500, 'swing'


class Notificator
    constructor: () ->
        @notifications = []
        @browserNotifications = false

        if window.Notification
            if Notification.permission == 'granted'
                @browserNotifications = 'html5'
            else
                if Notification.permission != 'denied'
                    Notification.requestPermission (permission) =>
                        if not Notification.permission
                            Notification.permission = permission
                        if permission == "granted"
                            @browserNotifications = 'html5'

    notify: (type, text, timeout) ->
        if @browserNotifications == 'html5'
            new Notification(text)
            return

        timeout ?= 7000
        for notification in @notifications
            do (notification) =>
                notification.moveUp(-50)
        notification = new AjentiNotification(type, text, timeout, this, 0)
        @notifications.push notification
        jQuery('#notifications').append notification.dom


window.Notificator = new Notificator()