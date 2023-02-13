define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_secretword.js  OKK");
 

//*************************************************************************************************************  
// Correction des mots secrets
//************************************************************************************************************* 

    $('.show_sort_correction').hide();
    $(document).on('keyup','.secret_letter', function(e) { 
         
          if (e.which == 32 || (65 <= e.which && e.which <= 65 + 25)
                            || (97 <= e.which && e.which <= 97 + 25)
                            || (192 == e.which) || (55 == e.which) || (50 == e.which)|| (57 == e.which) ) 
            {   
                let csrf_token    = $("input[name='csrfmiddlewaretoken']").val();
                let secret_letter = String.fromCharCode(e.which) ;
                let index         = $(this).data('index'); 
                let choice_id     = $(this).data("choice_id");
                let loop          = $(this).data("loop");                      
                let nb_tries      = $("#nb_tries"+loop).val();
                let position      = $("#position"+loop).val(); // Place de l'image de la fleur
                let word_length   = $("#word_length"+loop).val();
                let word_length_i = $("#word_length_i"+loop).val();
                let used_letter   = $("#used_letter"+loop).text(); 
                let score         = $("#score").val();

                $("#nb_tries"+loop).val( parseInt(nb_tries) - 1 ) ;
                if(  $("#nb_tries"+loop).val() == 1 )
                    { $('#win_sentence'+loop).html("<span class='text-danger'>Oh lààààà, il ne reste plus qu'une seule tentative.</span>"); }
                else 
                    {$('#win_sentence'+loop).html("");}
                
                $.ajax({
                        type: "POST",
                        dataType: "json",
                        data: {
                            'secret_letter': secret_letter,
                            'nb_tries'     : nb_tries,
                            'index'        : index,
                            'choice_id'    : choice_id,
                            'position'     : position,
                            'word_length'  : word_length,
                            'word_length_i': word_length_i,
                            'used_letter'  : used_letter,
                            'score'        : score,
                            csrfmiddlewaretoken: csrf_token,
                        },
                        url: "../../ajax_secret_letter",
                        success: function (data) {
     
                            if (data.response == "false")
                            {   
                                var new_position = parseInt(position) + 200;
                                $("#position"+loop).val(new_position);
                                $("#wordguess-counter"+loop).css("background-position","0 "+new_position+"px") ; 
                                $("#secret_letter"+index+"-"+loop).val('');
                                $("#secret_letter"+index+"-"+loop).focus() ;   

                                if (data.slide == 'yes'){
                                    var pxValue = currentSlide * slideWidth ; 
                                    this_slideBox.animate({
                                        'left' : -pxValue
                                    });
                                    currentSlide++ ;                                    
                                }
                            }
                            else {
                                $("#secret_letter"+index+"-"+loop).css('border','2px solid green');
                                $("#word_length"+loop).val(data.length);
                                var nidx      = parseInt(index)+1;
                                word_length_i = parseInt(word_length_i) ;
                                if (parseInt(index)+1 < word_length_i){ $("#secret_letter"+nidx+"-"+loop).focus(); } else {  $("#secret_letter0-"+loop).focus(); }  
                            }

                            $("#used_letter"+loop).text(data.used_letter);  
                            if (data.win == "true")
                            {      
                                $("#position"+loop).val(200);
                                $("#word_length_i"+loop).val(data.length_i);
                                $("#used_letter"+loop).text("");
                                $('#win_sentence'+loop).html("<span class='text-success'>BRAVO !<br/> Vous avez trouvé le mot caché. <br/>Cliquer sur le bouton bleu Valider.</span>");
                                $('#nav_start'+loop).show(500);
                                $('#word_left').text(data.nb);
                                $("#score").val(data.score);
                                $("#score_span").html(data.score);
                            }
                        }
     
                    })

            } 
    });







    });

});

 
