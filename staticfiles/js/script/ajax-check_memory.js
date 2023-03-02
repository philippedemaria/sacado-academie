define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_memory.js  OKK");



    //===========================================================================================   
    //=========================      DRAG & DROP      ===========================================
    //===========================================================================================  

    var card_ids = [] ; 
    $(document).on('click','.card', function(e) {  
            
            let length     = $("#length").val(); 
            $(this).toggleClass('is-flipped');
            card_ids.push( $(this).data('id') ) ;

            if (card_ids.length == length){ setTimeout(function() {  test_ajax_memo(card_ids,length)}  , 1000) ;  }
                            
        }) 

    function test_ajax_memo(liste,length){



            var div_width = $('#body_zone_exercise').width() ;
            var div_height = $('#body_zone_exercise').height() ;
            var slideWidth  = Math.floor(div_width);
            var slideHeight = Math.floor(div_height);

            $(".show_correction").width(slideWidth-40) ; 
            $(".show_correction").height(slideHeight) ;

        

            let csrf_token  = $("input[name='csrfmiddlewaretoken']").val();
            let numexo      = $("#numexo").val();
            let score       = $("#score").val() ;

                $.ajax({
                        type: "POST",
                        dataType: "json",
                        traditional : true,
                        data: {
                            'liste' : liste,
                            'length': length,
                            csrfmiddlewaretoken: csrf_token,
                        },
                        url: "../../ajax_memo",
                        success: function (data) {

                              

                            if (data.test == "yes")
                            {
                                
                                $("#score_span").text( parseInt(score) + 1 );
                                $("#score").val( parseInt(score) + 1 );

                                $(".card").each( function(index) {
                                    if ( $(this).hasClass('is-flipped') ){
                                        $(this).addClass('card_open'); 
                                    }
                                })

                            }
                            else
                            {
                                $(".card").each( function(index) {
                                    if ( $(this).hasClass('is-flipped') ){
                                        $(this).removeClass('is-flipped');

                                    }
                                })
                            }
                            card_ids = [] ; console.log(card_ids) ;
                            $("#numexo_span").text( parseInt(numexo) + 1 );
                            $("#numexo").val( parseInt(numexo) + 1 );
                        }
                    }) 
            }

 
    });

});

 
