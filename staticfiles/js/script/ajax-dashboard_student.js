define(['jquery', 'bootstrap', 'multislider' ], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-dashboard_student.js OK");
 

        var heights = $(".box").map(function ()
            {
                return $(this).height();
            }).get();

        maxHeight = Math.max.apply(null, heights) + 40;

        $(".over_box").css('height' ,maxHeight) ;


        $('body').css("overflow-x","hidden");
 
            var numItems = $('#mixedSlider .item').length ;
            var numItems_width = numItems * 350 ;
            var window_width = $( window ).width() ;

            if (numItems_width < window_width ) {

                $(".MS-controls").hide();

            }
            else 
            {

                $('#mixedSlider').multislider({
                    duration: 1000,
                    interval: 10000
                });

            }

    });        
});