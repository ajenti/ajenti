class window.Controls.dashboard__dash extends window.Control
    createDom: () ->
        """
            <div class="control container dashboard-dash">
                <div class="container widget-container container-0" data-index="0">
                </div>
                <div class="container widget-container container-1" data-index="1">
                </div>
                <div class="widget-storage"><children></div>
                <div class="container trash">
                    <i class="icon-trash"></i>
                </div>
            </div>
        """

    setupDom: (dom) ->
        super(dom)
        $(@dom).find('>.container').sortable({
            connectWith: '.dashboard-dash .container'
            handle: '.handle'
            revert: 200
            placeholder: 'placeholder'
            tolerance: 'pointer'
            start: () =>
                $(@dom).find('.trash').show()
            stop: () =>
                r = {}
                $(@dom).find('.trash').hide()
                $(@dom).find('.trash .control').remove()
                $(@dom).find('>.widget-container').each (i, c) =>
                    index = parseInt($(c).attr('data-index'))
                    r[index] = []
                    $(c).find('>*').each (i, e) =>
                        r[index].push(parseInt($(e).attr('data-uid')))
                @event('reorder', indexes: r)
        }).disableSelection()

        $(@dom).find('.widget-storage > *').each (i, e) =>
            $(@dom).find(".container-#{$(e).attr('data-container')}").append(e)


class window.Controls.dashboard__widget extends window.Control
    createDom: () ->
        """
            <div data-uid="#{@properties.uid}" data-container="#{@properties.container}" class="control dashboard-widget">
                <div class="handle"></div>
                <div class="content --child-container"><children></div>
            </div>
        """


class window.Controls.dashboard__header extends window.Control
    createDom: () ->
        """
            <div class="control dashboard-header">
                <div class="icon #{@s(@properties.platform)}">
                    <img class="image ubuntu" src="data:image/png;base64,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"/>
                    <img class="image debian" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAA0CAYAAADFeBvrAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wMHhYBBjTN8O8AAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAHMUlEQVRo3u1abUxU6RV+ZmD46CAfCoi4iriDtJrqWupmu2HdmFB/GFBT27RbyybbRH80a2OztKJJa0rTpqmiG//QVTYbNkutpCvZBtDKx6aiROIill211RGEQQEHBphhPrj3vvP0x96hUzIzcGcYKqYnmczkTs77vs85z3nPxwzwf5m/kEwimbWYe+qiBOQ1AB8AWAEgBsAkgIsAagC8BkAGsA7Auzqd7smz6o04kj8meY//ES/nln+S/AXJdHWd5GcBzMskHRpAhBLhA/e/ALKaZE2EAAIZwEHyryQLFy2GSG4F8BkAPQD6rTXz2el0Punt7b06ODg44HQ6PQ8ePBhyuVyKyWRakZeXl2symbalpKTkGAyGNL1e77+O/3rf0+l0f4m2Z35AUg5mcpfLNVRZWfl2YmLiKwDWA8gCkAEgGUCSelmsAbA5Pz9/x+HDh0tHRkY+C+GximiC2TVrYy9JrxBCtlqtXZ2dndVpaWmvAkiZ55J6AF8BsLm1tfVdRVGkIJTcEw0w+SSnA3mlvLz8LYPB8BKAtRFQObusrOxNIYQI4qlvLCggRVE6Zu8wOTlpvnjxYgUA4wJtYzxx4sRPAoDyKoryj4Xwik59/74/BYQQoqOj4z0ABQAyF5gMyW1tbaeDxFRpJGAMJLcBgMfj+a+gPXfu3DtqYEdLsm022+ezY0lRlHGSCZGURstI7vc3UV1d3XEAadHOc0VFRa/7U6+2tvbY1NRUX0dHR2IkXvqWP5ja2tpj6hW8GBJrs9l6fHt3dXXtPnDgwO7+/v7wjel2uz/0Waivr+9vANLDMEoMyTdIXiI5SPILkvUkf05yZSjdtra2Yz7KCSFcABIOHToUH45nsgBACOH2ATKbzWfCWCeB5IAQYqqzs/PXCQkJrwL4JoBNBQUFL3o8njKSLwfTz8jIyJp1OcSHmxbiSH7Hn24mk+lFjWCSSY7dvXv3o9TU1NcBrAqQVF84evToyjnShYckp6amBpuamuLDppssyzOtwPXr16u0WkYI8Wez2Vyvlj+hdGNCrTM0NHTNd47p6emtIYMuhHUzhRC5ACiEkC9fvlytFo3z9c4P3W73SyaTqQRA71zYQ1IlLk7yfa6pqbGG5Z3u7u7ViqK4SXolSXIAiNNYVVgbGhqOLMRV9/Tp08szzZIQjXMVhgFlYmJimiQA6CRJGgMgafDOxpiYmPRTp059pDHmdgdMhjrdDF3b29v/HpZVenp6Vqoe4vDwcKsWXavV+iNJkuyhDBZIzp49uynQc7vdfpMk3W73cHFx8dqwPCSEmIkvp9N5X8vBpqensyRJmgDg1aJ38ODBB4GeOxyOEQC4d+/eJw0NDYNhAdLr9Tq/ztOs5WBOp1MyGo1rSK7SSIyAtM7MzCxUqdczl5GCAnI4HF7frSZJkkXLqWw22yMAGBsb26QhfoxBnu+MjY1NAYC9e/d+PJ9uMaAsW7ZM7/NQfHy8Wwug8fHxR16vV46Njd01X53Ozs6YQKnD6/V+AgBXrlw52d/fPxL2VdnR0eG7ttnX1/eGRvUEu91ulmXZFqzHIllAsiBUcp2cnCwmyYcPHzYuX758dUR3f3Nz8wpZlt1qV/pHrfolJSXfVlPHpUDfFxYWpm3ZsiU1BAU3+3IPgPyIk9nx48fjZFl2qq2vUy0K551Prl69mlFfX/8b9UxlQXotXRD975L0kPRWVla+vWBzb5fLZSFJWZadWpqqkydPbhgdHf1adXX11sbGxt+roN4nmTjXrI/ke+qe7j179uzTMD2aW+7fv/8ntdyQ7Hb7VzWoGvbv35/c3d297tq1a7urqqp+poLqJ/k7kmtmtRdvkfzYN1EaGBho3b59+y6t5dacUlNTU+wroR4/frwzjPY97syZM7kOh6PqwoULv7Tb7f9SFMUeaAwmy/K4zWb7XKXYxlCFcySj4CRJkoYMBkOSoihfGAyGr4exhyE7O3v9+fPn123YsOGdioqK9+/cueMqKipalZ2dnTIxMeFqb28fHhwctHd1dY2qlflk1Jp6i8XS4tctyiSLwx22ANhosVh2OJ3OfRaLZd/t27dLTp8+vU6lVsyiTCmam5t/GmD0a4hk5qbOJZYDSA2XWpFIuizLLh/XrVbrrbq6uhgsZWloaKiY5aUdSxpQXl7eapfLNewDND4+/lsscdE1NTX9ym8+5sFzIJkDAwOf+qWOsiWPqKSk5BXf4ER9rV/qmGKPHDnypt8ExvxM/AwfoRibmpr+4Afq0vMQT1k3btw45xdPO58HT61taWmp9PPUrefBU9m1tbXHFEXx/ZD8hGTsUgeVnpubW+RwOB6poHrnauSWgugBbGtpaTkly/KUCuzWYv+1LCoUBFB48+bNDyRJmhBCjJDMJRm3WAfQRWndnJycnNzS0tIXysvLs4xGYxIAD4CHAD7V6XSjSw2Qj4aJas9jwJcjXDeACXz5B8CoyL8BKqXI0VsxVxQAAAAASUVORK5CYII="/>
                    <img class="image centos" src="data:image/png;base64,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"/>
                    <img class="image rhel" src="data:image/png;base64,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"/>
                    <img class="image freebsd" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAA0CAYAAADFeBvrAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QIREQ8nz2emKAAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAMzSURBVGje7dpPiNRlHMfx93d2NV0U/BNBuXWxpMRAw1rq0AZWFJ2KAulSh4IOQd68dO7qLYsipENBsBD+CywQLCQDay0jk7KWjazVsmjNVp19d5hnaJh5ZlabXZ1H9nPaGfb3Y177fZ59nvk+P5jPfObTTaLxhboM2Aq8BCwCTgAjwDvA98C5iKi2u5laAa5L164A1gEbgYGmX/0bGAXGgB/T6ylgOiLscO9FwCrgaeAJ4A6gCuwCtkTEz80XvWr7HFJfUFeri9W+dE2/ulRdqz6rvqtOeOk5q46oL6r3qcvVhWqoFXVAvVl9Rt3X4T6f5So0BSycoarjqWoHgF+B1cAjwAPATV2OmD+AQ8BHqYIV4HHgfmDtjMMtIppBFj1/IqLS9N6Zgj2SStqYnQWDjuRAbxUMej0H+go4WSCmCnyQA00CbxcI2gVMtIAi4gLwHvBbQZgLaapM5SoEcDytA6VkFPgkIqbbgf6pj8dCsjdtnciCIuIi8F1BoFPAdFuQ2g+sKQh0Y6MjN+QWAPcWBHoYWNIJtDJtNEvJ7cCdarSA0ptDwK0FgZYCw0BfrkL9CRSFLayPpi9/LaABYFOBO4W7geU50ALgrgJBlfp/5mbQqoJ32/dca6D1OdBwwaDBdnOo2JZCu4W16DSDTl5roOMFW07kQOMFg8ZyoLGCQZ/nQFXgaKGggznQOeDjAjFH02dvAZ0HPi0Q9D61Flx2HfoCOF0Q5iy1k5BqCygdNv0A7CkI9BPwZf2gLNf1mQTeLAj0GvB7p55CfZLtKADzDTCSOr7/behyUdcD+4FlPQx6LCL2dtr6NA69UWBLD2O25ZaYmXbbO4E3ehBzGNgREX9d9pXqRvWgvZNx9amu/hzqkDraA5gz6nP1pmK3qAfVb68iZkJ9flYHrvqQuv8qYA6rT87JbFRvU19J5b8S2Z6WkLmLukQdVvfMIWQyPQ5z5dZB9QZ1s3psFiF/qi+ra+rPE11266dLVB+1vvIQsJna01eDNJzZzJDp1A84AuwG9gGnI+L8/+5lzVK1IvX1rgduoXYksy79PAhsSMgJ4ENqR4nH0tf+r4FfgIvtHi+71PwLHQqrzsEuGrwAAAAASUVORK5CYII="/>
                    <img class="image arch" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAA0CAYAAADFeBvrAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QweFAkhkcbIRwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAU3SURBVGje3VpdaFNnGH7y18S2XizKlv7YsamMTUcj6yhYqrDGbTcreFXFshVEqDeCjtFejIRm82YX1lEY7EL3ywzmYhe9KEpbtlyVVGhV5kDRltj8NGh7kjQ5+Tknzy7WqitJc05M0mTPVQjv+d7v+Z73ffO+3wlQAZA8QPJgJXzpK+EkEAg4dDrdDgCf4P8APoep3L60FSDj2PicyWTGal2Zumg0Gt2QJxqNiiR31ywhQRA+TqfTz+JNlmU+evToTM2G3PLy8jmDwfDcmVYLg8FwrmbDTZKkLHPjjZojlEqlvs5Dhmtra95aU8eQTqelfIRkWSbJAzWTQ8lksl+v1+vyOtVqsbCwcIGkphbU0S0sLNxlAQiCEPP5fDuqnlA4HN5PhYhGo2ernlAsFvtTKSFJkuRqD7f9JJnNZqkCF6qZ0/7p6Wk1ZBgMBpdINlSjOjvXZ57piYkJVaR8Pt9H1Zg738iynCL5OYAJl8ulmJAoiqFqU6dx0x6n9uzZ8/vo6CglSVLK67OqISSK4q85uoGkx+P52+l0ZsPhcEE2T58+fUxyRzWo8+b6nJMX9+/flzKZjJICsf0j+uLi4ihLhEgksrDtbQ5LjxPbRkiW5WulZhOPx1cqcZmSS52DoihmSk0om80yEol8uh258xPLhJWVFV+l1dnF8uNMxQglk8k/ys1G+vcX2Vj2iZXkEaPReLTch6bT6XSiKA6VvUwHAgFPMYmucqTYyKVVkvVq9qhqpl9bW7M2NDTMqXnG5XLB4/GQJA4fPqw5deoUtFrlgRGPx79sbGy8WK7ceazmhHt7e6nRaK4BOAtgUKPR/NzV1SUXkVKvlCPcBtTsoK+vjwB6N0WBBkBXd3e3qhCMxWI/lnw8CIfDPqUbuH79OgH0bbFk99jYmJruIUXytZIRCgaDJ1SUW/b39/9ZaM1jx479pqQDf6FAXC0ZoXQ6LaoIDwL4UMGy7967d09t6XvnpX+HSF4yGAyKm8UbN25IAG4qML3rcrnCKsf8X16KEMnWRCKh6jLw9u3b80ptZ2dnt0z2UOi/Vw1Go/EQyfeLJhQMBr+or69X1coLgjCp1HZiYuKHAibZgYEBXLlyBclkEnV1dZonT558W2xlayqmBzt//vwJlX4KYnJy8oHVak2ePHmSDx8+jJHsVa1QKpUaL+YgWltboyoJFbTp6enZNzc3V3f8+PGre/fuXTx9+nSrWnU+yGQy2WIUGh8fP1NqhTbhu46OjkOqCIVCodli2/5bt265VJB5qxgfsiw/INmWa019DidHAXQo3ZQkSVheXsbS0hKmpqYwMzOTUPrs4ODg7ra2NvT09KClpQUWiwV6feE/t2i12n2yLP9F8ohGo5nb6sT0qVRKUHJK4XCYIyMj7OzslJqamgIAZgBcBGBVEQyW9WdmLBaLv7OzU7Lb7QyFQkq7EpHkrq06gqGtFkgkEvR6vbTZbAQQBjACoBNAKfqsV9fXsgMI2Ww2er1exuPxLUmtrq5ezqeOMRKJCHkuAOl0Omm1WpMAvABsFZj0bQC8VqtVHBkZoSAI+d6oiyR35irTX+VSZHh4mAAiAJwA2rfh+q99PRKEoaEhiqKYK3K+36zO6y8a+P1+OhwOms1mEcBwFb3oGDKbzUmHw0G/37+Z19vPrCKRyM2Nbx0OB00mUwCAA4AZ1QczAIfJZArY7fYXc8lDUguS7dFoNO12u9nc3Mx1IiZUP0wA7C0tLXS73YzFYpl4PP4e7ty5c8lqtUYAuAE0o/bQAsDd3t4em5+fv/wPuh5qje4T9gsAAAAASUVORK5CYII="/>
                    
                    <div class="bar">#{@s(@properties.platform)}</div>
                </div>

                <div class="labels">
                    <div class="hostname">#{@s(@properties.hostname)}</div>
                    <div class="distro">#{@s(@properties.distro)}</div>
                </div>

                <div class="inner"><children></div>
            </div>
        """


class window.Controls.dashboard__welcome extends window.Control
    createDom: () ->
        """
            <div class="control container welcome">
                Welcome to Ajenti.<br/>
                Use the <b>Feedback</b> link to send us your suggestions!<br/>

                <br/>
                Follow @ajenti for news and announcements.</br>
                
                <iframe allowtransparency="true" frameborder="0" scrolling="no" src="//platform.twitter.com/widgets/follow_button.html?screen_name=ajenti&show_count=true&dnt=true" style="width:300px; height:20px;"></iframe>
                <br/>
                <br/>

                <a href="mailto:e@ajenti.org">Send e-mail</a> if you have private/security questions or issues.<br/>
                <br/>
                <b>Don't forget to change default password in the Configurator!</b>
            </div>
        """
