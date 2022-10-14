define(['jquery', 'bootstrap'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-avatar.js OK");

    


        $(".choicer_avatar").on('click', function (event) {

            let url = $(this).data("url");
            $("#id_avatar").val(url);
            $(".choicer_avatar").addClass("list_avatar_opaque");
            $(this).removeClass("list_avatar_opaque");

        }); 



 

        $(".choicer_backtitle").on('click', function (event) {

            let url = $(this).data("url");
            $("#id_backtitle").val(url);
            $(".choicer_backtitle").addClass("list_avatar_opaque");
            $(this).removeClass("list_avatar_opaque");

        });        
  


});

});

