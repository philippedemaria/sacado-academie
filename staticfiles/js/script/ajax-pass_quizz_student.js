define(['jquery',  'bootstrap', 'ui' , 'ui_sortable' , 'uploader','config_toggle'], function ($) {
    $(document).ready(function () {

        console.log(" ajax-ajax-pass_quizz_student chargé ");


        $("#show_retroaction").on('click', function (event) {


            let question_id = $("#question_id").val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'question_id': question_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../ajax_show_retroaction",
                    success: function (data) {
 
                        choices = data["choices"] ; 

                        if (choices.length >0)
                        { for (let i = 0; i < choices.length; i++) {
                                    
                                let choices_id = choices[i][0];
                                let choices_retroaction =  choices[i][1]  ;
                   
                                if ($("#solution"+choices_id).is(":checked"))
                                        {   
                                            $('#ans_retroaction'+choices_id).html(choices_retroaction);
                                        }                     
                            }
                        }

                        $('#button_submit_div').html("").html("<button type='submit' class='btn btn-primary'><i class='fa fa-caret-right'></i> Question suivante</button>") ;

                    }
                }
            )
         });



        $("#start_positionnement").prop("disabled",true) ;

        $("body").on("change","#last_name", function (event) {

                $("#start_positionnement").prop("disabled",false)


            }) 








 
    });
});