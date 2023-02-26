define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-support_creator_create.js  OKK");

 
        $('[type=checkbox]').prop('checked', false); 
         
        qtype = $("#qtype").val();
        if (qtype<100){
            $("#id_situation").val(1);
        }
        $('#on_mark').hide();

        $('#id_is_publish').prop('checked', true); 
});

});

 
