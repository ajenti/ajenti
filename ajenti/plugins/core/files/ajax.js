function ajaxForm(formId, action)
{
    form = document.getElementById(formId);
    if (form)
    {
        params = "action=" + encodeURIComponent(action);

        var inputs = form.getElementsByTagName("input");
        url = inputs[0].value;
        if (inputs) {
            for (i=1; i<inputs.length; i++) {
                if (inputs[i].type == "text" || inputs[i].type == "password" || inputs[i].type == "hidden") {
                    params += "&" + inputs[i].name + "=" + encodeURIComponent(inputs[i].value);
                }
                if (inputs[i].type == "checkbox") {
                    if (inputs[i].checked)
                        params += "&" + inputs[i].name + "=1";
                    else
                        params += "&" + inputs[i].name + "=0";
                }
                if (inputs[i].type == "radio") {
                    if (inputs[i].checked) {
                        params += "&" + inputs[i].name + "=" + encodeURIComponent(inputs[i].value);
                    }
                }
            }
        }

        inputs = form.getElementsByTagName("select");
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                var sel = inputs[i];
                params += "&" + sel.name + "=" + encodeURIComponent(sel.options[sel.selectedIndex].value);
            }
        }

        inputs = form.getElementsByTagName("textarea");
        if (inputs) {
            for (i=0; i<inputs.length; i++) {
                var ta = inputs[i];
                params += "&" + ta.name + "=" + encodeURIComponent(ta.value);
            }
        }

        inputs = form.getElementsByClassName("ui-el-sortlist")[0];
        if (inputs) {
            params += "&" + inputs.id + "=" + ui_dumpSortList(inputs.id);
        }

        ajaxPOST(url, params);
    }
    return false;
}
