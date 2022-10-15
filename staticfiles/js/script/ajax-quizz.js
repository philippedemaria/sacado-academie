define(['jquery',  'bootstrap', 'ui' , 'ui_sortable' , 'uploader','config_toggle'], function ($) {
    $(document).ready(function () {


    console.log(" ajax-quizz chargé ");


    $('.confirm_create_historic').on('click', function (event) {
        if (!confirm('En créant cette présentation, vous allez créer son historique accessible ci-contre après la présentation')) return false;
    }) ; 



    $("#loading").hide(500); 

  // Affiche dans la modal la liste des élèves du groupe sélectionné
    $('#id_levels').on('change', function (event) {
        let id_level = $(this).val();
        let id_subject = $("#id_subject").val();
        let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
        $("#loading").html("<i class='fa fa-spinner fa-pulse fa-fw'></i>");
        $("#loading").show(); 
        $.ajax(
            {
                type: "POST",
                dataType: "json",
                traditional: true,
                data: {
                    'id_level': id_level,
                    'id_subject': id_subject,                        
                    csrfmiddlewaretoken: csrf_token
                },
                url : "../../qcm/ajax/chargethemes_parcours",
                success: function (data) {

                    themes = data["themes"];
                    $('select[name=themes]').empty("");
                    if (themes.length >0)

                    { for (let i = 0; i < themes.length; i++) {
                                

                                console.log(themes[i]);
                                let themes_id = themes[i][0];
                                let themes_name =  themes[i][1]  ;
                                let option = $("<option>", {
                                    'value': Number(themes_id),
                                    'html': themes_name
                                });
                                $('select[name=themes]').append(option);
                            }
                    }
                    else
                    {
                        let option = $("<option>", {
                            'value': 0,
                            'html': "Aucun contenu disponible"
                        });
                        $('select[name=themes]').append(option);
                    }
                    $("#loading").hide(500); 
                }
            }
        )
    });


    $('input[name=waitings]').on('click', function (event) {

            let waitings = $(this).val();
            let id_subject = $("#id_subject").val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $("#loading").html("<i class='fa fa-spinner fa-pulse fa-fw'></i>");
            $("#loading").show(); 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional: true,
                    data: {
                        'waitings': waitings,                     
                        csrfmiddlewaretoken: csrf_token
                    },
                    url : "../../tool/ajax_chargeknowledges",
                    success: function (data) {

                        knowledges = data["knowledges"];
                        for (let i = 0; i < knowledges.length; i++) {
                                
                                let knowledges_id = knowledges[i][0];
                                
                                $('hidden_knowledges').hide(500);
                                $('knowledge'+knowledges_id).show(500);
                            }
                      
                        $("#loading").hide(500); 
                    }
                }
            )
    });


    // Fonction de sélection du Vrai faux
    function checked_vf(){ 
            if( $("#check1").hasClass("checked")  )  
                {   
                    // Gestion du check
                    $('#check1').removeClass("checked");
                    $('#check2').addClass("checked");
                    // affiche du fa
                    $('#check1').css("display","none");
                    $('#noCheck1').css("display","block");
                    $('#check2').css("display","block");
                    $('#noCheck2').css("display","none");
                    $("#id_is_correct").prop("checked", false); 
                } 
            else 
                {   
                    // Gestion du check
                    $('#check1').addClass("checked");
                    $('#check2').removeClass("checked");
                    // affiche du fa
                    $('#check2').css("display","none");
                    $('#noCheck2').css("display","block");
                    $('#check1').css("display","block");
                    $('#noCheck1').css("display","none");
                    $("#id_is_correct").prop("checked", true); 
                }             
        }

        $('body').on('click', '#vf_zone1' , function (event) {  
            checked_vf() ;
        }); 
        $('body').on('click', '#vf_zone2' , function (event) {  
            checked_vf() ;
        }); 

 


        $("#id_calculator").prop("checked", false);   
        $("#id_is_publish").prop("checked", true); 


        $('body').on('click', '#checking_zone0' , function (event) {  
            checked_and_checked(0) ;
        });
        $('body').on('click', '#checking_zone1' , function (event) {  
            checked_and_checked(1) ;
        });
        $('body').on('click', '#checking_zone2' , function (event) {  
            checked_and_checked(2) ;
        });
        $('body').on('click', '#checking_zone3' , function (event) {  
            checked_and_checked(3) ;
        });


        function checked_and_checked(nb){ 
                qtype = $("#qtype").val() ;

                if( $("#check"+nb).hasClass("checked")  )  
                    {   
                        $('#check'+nb).removeClass("checked");
                        $('#check'+nb).css("display","none");
                        $('#noCheck'+nb).css("display","block");
                        $("#id_choices-"+nb+"-is_correct").prop("checked", false);                         

                    } 
                else 
                    {   
                        $('#check'+nb).addClass("checked");
                        $('#check'+nb).css("display","block");
                        $('#noCheck'+nb).css("display","none");
                        $("#id_choices-"+nb+"-is_correct").prop("checked", true);                     
                    }
 
                if (qtype==4 && $(".checked").length > 1 ) { 
                    alert("Vous avez choisi un QCS dans lequel une seule réponse est autorisée. Optez pour le QCM alors.") ; 
                    $('#check'+nb).removeClass("checked");
                    $('#check'+nb).css("display","none");
                    $('#noCheck'+nb).css("display","block");
                    $("#id_choices-"+nb+"-is_correct").prop("checked", false);                         
                    return false;
                }
            }
 

        // Sélectionne la couleur de fond lorsque la réponse est écrite
        function change_bg_and_select( nb, classe ){

            $('body').on('keyup', "#id_choices-"+nb+"-answer" , function (event) {   
                
                var comment =  $("#id_choices-"+nb+"-answer").val()  ;

                if ( comment.length > 0 )
                { 
                  $("#answer"+nb+"_div").addClass(classe) ; 
                  $("#id_choices-"+nb+"-answer").css("color","white") ;
                }
                else
                {
                   $("#answer"+nb+"_div").removeClass(classe) ; 
                  $("#id_choices-"+nb+"-answer").css("color","#666") ;
                }
             });
        }

 

           var arr = [ "bgcolorRed","bgcolorBlue","bgcolorOrange","bgcolorGreen"];  
            $.each(arr , function (index, value){  
                change_bg_and_select( index,  value );
            });

 
       // Trie des diapositives
        $('#questions_sortable_list').sortable({
            start: function( event, ui ) { 
                   $(ui.item).css("box-shadow", "2px 1px 2px gray").css("background-color", "#271942").css("color", "#FFF"); 
               },
            stop: function (event, ui) {

                var valeurs = "";
                         
                $(".sorted_question_id").each(function() {
                    let this_question_id = $(this).val();
                    valeurs = valeurs + this_question_id +"-";
                });


                $(ui.item).css("box-shadow", "0px 0px 0px transparent").css("background-color", "#dbcdf7").css("color", "#271942"); 

                $.ajax({
                        data:   { 'valeurs': valeurs ,   } ,   
                        type: "POST",
                        dataType: "json",
                        url: "../../question_sorter" 
                    }); 
                }
            });
 
       // Prévisualisation des images
        $("#id_imagefile").withDropZone("#drop_zone", {
            action: {
              name: "image",
              params: {
                preview: true,
              }
            },
          });


        // Chargement d'une image dans la réponse possible.
        $('body').on('change', '#id_choices-0-imageanswer' , function (event) {  
            previewFile(0,"bgcolorRed") ;
         });

        $('body').on('change', '#id_choices-1-imageanswer' , function (event) {   
            previewFile(1,"bgcolorBlue") ;
         });
 
        $('body').on('change', '#id_choices-2-imageanswer' , function (event) {   
            previewFile(2,"bgcolorOrange") ;
         });
 
        $('body').on('change', '#id_choices-3-imageanswer' , function (event) {   
            previewFile(3,"bgcolorGreen") ;
         });      

 
        function previewFile(nb,classe) {

            const preview = $('#preview'+nb);
            const file = $('#id_choices-'+nb+'-imageanswer')[0].files[0];
            const reader = new FileReader();


            $("#preview"+nb).val("") ;  
            $("#answer"+nb+"_div").addClass(classe) ;
            $("#id_choices-"+nb+"-answer").addClass("preview") ;
            $("#preview"+nb).removeClass("preview") ; 
            $("#delete_img"+nb).removeClass("preview") ; 

            reader.addEventListener("load", function (e) {
                                                var image = e.target.result ; 
                                                $("#preview"+nb).attr("src", image );
                                            }) ;

            if (file) { 
              reader.readAsDataURL(file);
            }            

          }
 
         
        // Chargement d'une image dans la réponse possible.
        $('body').on('click', '#delete_img0' , function (event) {  
            noPreviewFile(0,"bgcolorRed") ;
         });

        $('body').on('click', '#delete_img1' , function (event) {   
            noPreviewFile(1,"bgcolorBlue") ;
         });
 
        $('body').on('click', '#delete_img2' , function (event) {   
            noPreviewFile(2,"bgcolorOrange") ;
         });
 
        $('body').on('click', '#delete_img3' , function (event) {   
            noPreviewFile(3,"bgcolorGreen") ;
         }); 


        function noPreviewFile(nb,classe) {

                $("#preview"+nb).attr("src", "" );
                $("#answer"+nb+"_div").removeClass(classe) ;
                $("#id_choices-"+nb+"-answer").removeClass("preview") ;
                $("#preview"+nb).addClass("preview") ; 
                $("#delete_img"+nb).addClass("preview") ;      
          }

 

        $("#support_image").on('click', function (event) {

            get_the_target("#support_image","#drop_zone_image","#video_div","#audio_div")

        })



        $("#support_video").on('click', function (event) { 

            get_the_target("#support_video","#video_div","#drop_zone_image","#audio_div")

        })



        $("#support_audio").on('click', function (event) { 

            get_the_target("#support_audio","#audio_div","#drop_zone_image","#video_div")

        })


        $("#support_audio_image").on('click', function (event) { 

            get_the_target_2("#support_audio_image","#drop_zone_image","#audio_div","#video_div")

        })



 
        function get_the_target(target,cible,f1,f2){

            $(f1).removeClass("allowed_display");
            $(f2).removeClass("allowed_display");
            $(f1).addClass("not_allowed_display");
            $(f2).addClass("not_allowed_display");

            if ($(cible).hasClass("not_allowed_display")) 
            {
                $(cible).removeClass("not_allowed_display");
                $(cible).addClass("allowed_display");
            } else {
                $(cible).removeClass("allowed_display");                
                $(cible).addClass("not_allowed_display");
            }
        }

        function get_the_target_2(target,cible,f1,f2){

            $(f1).removeClass("allowed_display");
            $(f2).removeClass("allowed_display");
            $(f1).addClass("not_allowed_display");
            $(f2).addClass("not_allowed_display");

            if ($(cible).hasClass("not_allowed_display")) 
            {
                $(cible).removeClass("not_allowed_display");
                $(cible).addClass("allowed_display");
                $(f1).removeClass("not_allowed_display");
                $(f1).addClass("allowed_display");
            } else {
                $(cible).removeClass("allowed_display");                
                $(cible).addClass("not_allowed_display");
                $(f1).removeClass("not_allowed_display");
                $(f1).addClass("allowed_display");
            }
        }



        $("#this_question_display_overview").on('click', function (event) {

            let type = $("#qtype").val(); 

            let title      = $("#id_title").val();
            let fontsize   = $("#id_size").val();
            let calculator = $("#id_calculator").val();
            let duration   = $("#id_duration").val();
            let theme      = $("#id_theme").is(":checked"); // booleen
            let audio      = $("#id_audio").val();  
            let video      = $("#id_video").val(); 
            let preview    = $("#drop_zone img")[0]; 
            let imagefile  = $("#id_imagefile").val(); 

            $("#overview_text").html(title);
            $("#overview_text").css("font-size",fontsize);
            $("#overview_duration").html(duration);
            MathJax.Hub.Queue(['Typeset',MathJax.Hub,'overview_text']);

            let qcm ;

            if (type == 1 )
            {
                let true_false = "<div class='col-sm-12 col-md-6  bgcolorBlue white'  align='center' style='border-radius : 10px'><h1 style='font-size:3.5em' class='thin'>VRAI </h1></div><div class='col-sm-12 col-md-6  bgcolorRed white'  align='center' style='border-radius : 10px'><h1 style='font-size:3.5em' class='thin'>FAUX </h1></div>"
                $("#overview_answers").html("").append(true_false);

            }
            else if (type > 2 )
            {
                let choice0 = $("#id_choices-0-answer").val();
                let choice1 = $("#id_choices-1-answer").val();
                let choice2 = $("#id_choices-2-answer").val();
                let choice3 = $("#id_choices-3-answer").val();
                if (theme) {  
                    qcm = "<div class='col-sm-12 col-md-6'   style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice0)+"em' class='thin'>"+choice0 +" </h1></div><div class='col-sm-12 col-md-6'   style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice1)+"em' class='thin'>"+choice1 +" </h1></div>"
                    qcm = qcm + "<div class='col-sm-12 col-md-6'  style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice2)+"em' class='thin'>"+choice2 +" </h1></div><div class='col-sm-12 col-md-6'  style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice3)+"em' class='thin'>"+choice3 +" </h1></div>"  
                }
                else{ console.log("no theme") ;
                    qcm = "<div class='col-sm-12 col-md-6  bgcolorBlue white'  style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice0)+"em' class='thin'>"+choice0 +" </h1></div><div class='col-sm-12 col-md-6  bgcolorRed white' style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice1)+"em' class='thin'>"+choice1 +" </h1></div>"
                    qcm = qcm + "<div class='col-sm-12 col-md-6  bgcolorOrange white'   style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice2)+"em' class='thin'>"+choice2 +" </h1></div><div class='col-sm-12 col-md-6  bgcolorGreen white' style='border-radius : 10px'><h1 style='font-size:"+asnwerfontsize(choice3)+"em' class='thin'>"+choice3 +" </h1></div>"  
                }

                $("#overview_answers").html("").append(qcm);
                MathJax.Hub.Queue(['Typeset',MathJax.Hub,'overview_answers']);
            }


 
            if (audio)
            {
                let overview_audio = "<audio controls><source src='#' type='audio/mpeg'></audio>"
                $("#overview_audio").html("").append(overview_audio);
            }

            if (video)
            {
                $("#overview_video").html("").append(video);
                MathJax.Hub.Queue(['Typeset',MathJax.Hub,'overview_video']); 
            }

            if (imagefile)
            {
                let size_img ;
                if (type == 2 ){ size_img = 550+"px" ;  } else { size_img = 350+"px" ;  }  
                overviewpreviewFile();  
                $("#overview_imagefile").attr("width", size_img );
            }
            else 
            {
 
                if ( $("#drop_zone img")[0] ) 
                    {   
                        let size_img ;
                        if (type == 2 ){ size_img = 550+"px" ;  } else { size_img = 350+"px" ;  }  
                        $("#overview_imagefile").attr("width", size_img ).attr("src", $("#drop_zone img")[0].currentSrc );
                    }
 
            }


            let file0 = $("#preview0").attr('src') ;
            let file1 = $("#preview1").attr('src') ;
            let file2 = $("#preview2").attr('src') ;
            let file3 = $("#preview3").attr('src') ;

            if (file0)
            {

 
                if (theme) {  
                    qcm = "<div class='col-sm-12 col-md-6'   style='border-radius : 10px'>"
                    if(file0) { qcm = qcm +"<img src='"+file0+"' height='90px' id='id_choices-0' />"}
                    qcm = qcm +"</div><div class='col-sm-12 col-md-6'   style='border-radius : 10px'>"
                    if(file2) { qcm = qcm +"<img src='"+file2+"' height='90px' id='id_choices-1' />"}
                    qcm = qcm +"</div><div class='col-sm-12 col-md-6'  style='border-radius : 10px'>"
                    if(file1) { qcm = qcm + "<img src='"+file1+"' height='90px' id='id_choices-2' />"}
                    qcm = qcm + "</div><div class='col-sm-12 col-md-6'  style='border-radius : 10px'>"
                    if(file3) { qcm = qcm + "<img  src='"+file3+"' height='90px' id='id_choices-3' />"}
                    qcm = qcm + "</div>"  
                }
                else{ 
 
                    qcm = "<div class='col-sm-12 col-md-6 bgcolorRed white'   style='border-radius : 10px'>"
                    if(file0) { qcm = qcm +"<img src='"+file0+"' height='90px' id='id_choices-0' />"}
                    qcm = qcm +"</div><div class='col-sm-12 col-md-6 bgcolorBlue white'   style='border-radius : 10px'>"
                    if(file2) { qcm = qcm +"<img src='"+file2+"' height='90px' id='id_choices-1' />"}
                    qcm = qcm +"</div><div class='col-sm-12 col-md-6  bgcolorOrange white'  style='border-radius : 10px'>"
                    if(file1) { qcm = qcm + "<img src='"+file1+"' height='90px' id='id_choices-2' />"}
                    qcm = qcm + "</div><div class='col-sm-12 col-md-6 bgcolorGreen white'  style='border-radius : 10px'>"
                    if(file3) { qcm = qcm + "<img  src='"+file3+"' height='90px' id='id_choices-3' />"}
                    qcm = qcm + "</div>"
                }


            }
 
 
            
        })





        function overviewpreviewFile() {

            const file = $('#id_imagefile')[0].files[0];
            const reader = new FileReader();

            reader.addEventListener("load", function (e) {
                                                var image = e.target.result ; 
                                                $("#overview_imagefile").attr("src", image );
                                            }) ;

            if (file) { console.log(file) ;
              reader.readAsDataURL(file);
            }            

          }

        function asnwerfontsize(choice) {

            let fs ;
            if ( choice.length > 50) { fs = 1.2 ;}
            else if ( choice.length > 17) { fs = 1.7 ;}
            else if ( choice.length > 10) { fs = 2.5 ;}
            else { fs = 3 ;}

            return fs;
        }




        // Chargement d'une image dans la réponse possible.
        $('body').on('click', '.automatic_insertion' , function (event) {  
 
            var feed_back = $(this).attr('id');
            $("#div_"+feed_back).toggle(500);

         });








 
    });
});