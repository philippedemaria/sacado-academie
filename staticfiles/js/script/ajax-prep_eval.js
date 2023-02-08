define(['jquery', 'bootstrap','ui'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-prep_eval.js OK");

        $( "#datepicker" ).datepicker({ minDate:0,dateFormat: "yy-mm-dd",dayNames: [ "Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa" ]});

        $(document).on("change", "#datepicker" , function(){ 
                var selected = $(this).val();
                $('#id_date').val(selected);
                var this_date = selected.split("-");
                months = ["","janvier", "février", "avril", "mai", "juin", "Juillet", "août", "septembre", "octobre", "novembre", "décembre", ]
                this_day = this_date[2] + " " +months[parseInt(this_date[1])] +" "+ this_date[0]
                $("#madate").html(this_day);
            });



        $(document).on('click', '.selector_theme', function (event) {

                $(this).find('input').attr('checked',true);
                var myStr = $("#mesthemes").html();
                var mySearch = $(this).text().trim();
                var p_id = $(this).data("parcours_id");

                if ($(this).hasClass('selector_theme_selected')) { 
                    $(this).removeClass('selector_theme_selected') ; 
                    $(this).find('input').attr('checked',false); 

                    if ( myStr.indexOf(mySearch) != -1 ) {  
                        $("#liste"+p_id).remove()
                    };
                } 
                else { 
                    $(this).addClass('selector_theme_selected') ; 
                    $(this).find('input').attr('checked',true);

                    if ( myStr.indexOf(mySearch) == -1 ) {  
                        $("#mesthemes").append( "<ol id='liste"+p_id+"'>"+mySearch+"</ol>" );
                    };
 
                } 
         });



        var slideBox = $('.slider_prepeval ul'),
            slideWidth = 610 ,
            slideQuantity = $('.slider_prepeval ul').children('li').length,
            currentSlide = 1 ;

        slideBox.css('width', slideWidth*slideQuantity);

       $(document).on('click', '.prep_eval_nav' ,function(){ 

               var whichButton = $(this).data('nav'); 

                   if (whichButton === 'next') {

                        if (currentSlide === slideQuantity)
                            { 
                                currentSlide = 1 ;                                     
                                
                            }
                        else 
                            { 
                                currentSlide++ ; 
                            }



                   } else if (whichButton === 'prev') {

                        if (currentSlide === 1)
                            { 
                                currentSlide = slideQuantity ;                                     
 
                            }
                        else 
                            { 
                                currentSlide-- ; 
                            }
                   }

                var pxValue = -(currentSlide -1) * slideWidth ;
                slideBox.animate({'left' : pxValue})

            });

       $(document).on('click','.prep_day',function(){


            var loop = $(this).data("panel");
            $(".panels").addClass('no_visu_on_load') ;
            $(".panels").removeClass('this_panel') ;

            $("#panel"+loop).removeClass('no_visu_on_load') ;
            $("#panel"+loop).addClass('this_panel') ;




       })



    });

});

