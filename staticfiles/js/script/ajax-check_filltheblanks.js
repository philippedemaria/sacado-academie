define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_filltheblanks.js  OKK");


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
                    word = $(ui.draggable[0]).data("word") ;  

                    var subloop = $(this).data('subloop');  
                    $("#loop_"+loop+"-"+subloop).val(word);

                    $(ui.draggable[0]).removeClass('word_choice');
                    $(this).addClass('input_droppable_no_width');
                    $(this).removeClass('input_droppable');
                    $(this).removeClass('input_droppable_big');

                    
                },
                over: function(event, ui) {
                    $(this).addClass('input_droppable_big');
                },
                out: function(event, ui) {
                    $(this).removeClass('input_droppable_big');
                    $(this).addClass('input_droppable');
                    this_answer = $(ui.draggable[0]).data("subchoice") ;
                    old_list = $(this).find('input').val()  ;  
                    word = $(ui.draggable[0]).data("word"); 
                }
        });

    })


     $( document ).on('mouseover', ".eraser" , function () {
        var loop = $(this).data('loop'); 
        });


 


//*************************************************************************************************************  
// Correction des filltheblanks
//************************************************************************************************************* 
  
    $(document).on('click', ".show_filltheblanks_correction" , function (event) {
 

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
            form_data.append("csrfmiddlewaretoken" , csrf_token);

            let supportfile_id = $(this).data("supportfile_id") ;
            let loop           = $(this).data("loop") ;
            form_data.append("supportfile_id" , supportfile_id); 
            form_data.append("loop" , loop); 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: form_data,
                    url: "../../check_filltheblanks_answers",
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

 
