define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_image.js  OKK");

 
//===========================================================================================   
//=========================      DRAG & DROP      ===========================================
//===========================================================================================  

            $( document ).on('mouseover', ".draggable" , function () { 
                var loop = $(this).data('loop');
                $( this ).draggable({
                        containment: ".dropzone"+loop ,
                        appendTo : '.droppable'+loop , 
                        revert : true,
                    });

                $( ".droppable"+loop ).droppable({
                        drop: function( event, ui ) {
                            $(this).append( $(ui.draggable[0])  );
                            this_answer = $(ui.draggable[0]).text().replace(" ","");
                            ta =  $.trim(this_answer) ;
                            $(this).next().val(ta);
                            $(ui.draggable[0]).removeClass('quizz_choice')
                        },
                        over: function(event, ui) {
                            $(this).css('background-color', '#e8fff2');
                        },
                        out: function(event, ui) {
                            $(this).find('input').val("")  ; 
                             $(this).css('background-color', 'white');
                            $(ui.draggable[0]).addClass('quizz_choice') 
                        }
                });

            })

            $( document ).on('mouseover', ".drag_x" , function () { 

                $( this ).draggable({ axis: "x" , containment:  'parent' });
            })



//*************************************************************************************************************  
// Récupération des Vrai/Faux
//************************************************************************************************************* 

    $(document).on('click', ".show_image_correction" , function () {



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
            let loop           = $(this).data("loop") ;


            form_data.append("csrfmiddlewaretoken" , csrf_token);            
            form_data.append("supportfile_id" , supportfile_id); 
            form_data.append("loop" , loop); 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: form_data ,
                    url: "../../check_image_answers",
                    success: function (data) {
                        $("#score").val(data.score);
                        $("#numexo").val(data.numexo);
                        $("#score_span").html(data.score);
                        $("#numexo_span").html(data.numexo);
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

 
