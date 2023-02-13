define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_grid.js  OKK");



//*************************************************************************************************************  
// Correction des mots mélés
//************************************************************************************************************* 
  
    var liste = [] ; 
    $(document).on('mousedown','.clickable', function(e) {

            code    = $(this).data('code') ;
            encoder = $("#encodeur").val() ;
     
            if ( $(this).hasClass("highlight") )
                {
                    $(this).removeClass("highlight") ;
                    idx = liste.indexOf(  $(this).text() ) ;
                    if(idx>-1)
                    {  
                        liste.splice(idx, 1) ;
                        $("#encodeur").val( parseInt(encoder) - parseInt(code) );
                        sender  = $("#encodeur").val() ;
                    }


                }
            else
                { 

                    $("#encodeur").val( parseInt(encoder) + parseInt(code) );
                    sender  = $("#encodeur").val() ;

                    $(this).addClass("highlight") ;
                    liste.push($(this).text());
                    text = liste.join("");

                    $(".these_words").each( function(index) {

                        let word = $("#word"+index).val() ; 
                        let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                        if ( text == word ){

                            liste = [] ;

                            let score  = $("#score").val()   ; 

                            $.ajax(
                                {
                                    type: "POST",
                                    dataType: "json",
                                    traditional : true,
                                    data: {
                                        'sender' : sender,
                                        'word'   : word,
                                        'score'  : score,
                                        csrfmiddlewaretoken: csrf_token,
                                    },
                                    url: "../../check_grid_answers",
                                    success: function (data) {
                                        //********** Gestion de la div de solution ********************
                                        $("#score").val( data.score);                            
                                        $("#score_span").html( data.score );
                                        $("#encodeur").val( 0 );
                                        if (data.true == "yes" ) 
                                            {
                                                $("#check"+index).html("<i class='fa fa-check text-success'></i>");
                                                $(".highlight").removeClass("clickable");
                                                $(".highlight").addClass("highlight_win");
                                                $(".highlight").removeClass("highlight");
                                            }
                                        else{
                                            $(".highlight").addClass("highlight_red");
                                            setTimeout(function(){
                                            $('.highlight').removeClass("highlight").removeClass("highlight_red");
                                                    },500);
                                        }
                                        //*************************************************************
                                        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);    
                                    }
                                })
                        }
                        else if (text.length > 8) { 
                            if ($('#grid td').hasClass("highlight"))
                            {
                                liste = [] ;
                                $('.highlight').addClass("highlight_red")  ;

                                setTimeout(function(){
                                            $('.highlight').removeClass("highlight").removeClass("highlight_red");
                                                    },500);

                                $("#encodeur").val( 0 ); 
                            }
                        }

                    })
                }
        });

    $(document).on('click', ".show_grid_correction" , function (event) {
 

            var div_width = $('#body_zone_exercise').width() ;
            var div_height = $('#body_zone_exercise').height() ;
            var slideWidth  = Math.floor(div_width);
            var slideHeight = Math.floor(div_height);

            $(".show_correction").width(slideWidth-40) ; 
            $(".show_correction").height(slideHeight) ;




            event.preventDefault();   
            my_form = document.querySelector("#all_types_form");
            var form_data = new FormData(my_form); 
 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let supportfile_id = $(this).data("supportfile_id") ;

            form_data.append("csrfmiddlewaretoken" , csrf_token);            
            form_data.append("supportfile_id" , supportfile_id); 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: form_data,
                    url: "../../check_grid_answers",
                    success: function (data) {
                        //********** Gestion de la div de solution ********************
                        $("#show_correction"+loop).show(500);
                        $("#this_correction_text"+loop).html(data.this_correction_text);
                        $("#message_correction"+loop).html(data.msg);
                        //*************************************************************
                        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);    
                    },
                        cache: false,
                        contentType: false,
                        processData: false
                }
            )
         });









    });

});

 
