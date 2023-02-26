define(['jquery', 'bootstrap', 'ui','ckeditor'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-support_creator_canvas.js");


        $(document).on('change', '.this_variable' , function(event){
            $(this).addClass('this_variable_active');
        });  

        if (!$(".this_variable").is(':empty')  ) {$(".this_variable").addClass('this_variable_active');}

        //**************************************************************************************************************
        //********            ckEditor            **********************************************************************
        //**************************************************************************************************************

        CKEDITOR.replace('title', {
                height: '100px' ,
                filebrowserBrowseUrl : '/ckeditor/browse/',
                filebrowserUploadUrl : '/ckeditor/browse/',    
                toolbar:    
                    [  
                        { name: 'paragraph',  items: [ 'NumberedList', 'BulletedList', '-',   'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] }, 
                        { name: 'basicstyles',  items: [ 'Bold', 'Italic', 'Underline',  ] },
                        { name: 'insert', items: [ 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar','Iframe']},
                    ] ,
            });


   
        //*************************************************************************************************************
        //*************************************************************************************************************
        //*************************************************************************************************************  
        $('select[name=subject]').on('change', function (event) {
            let subject_id = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'subject_id': subject_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_get_skills",
                    success: function (data) {
                        
                        skills = data["skills"]
                        $('select[name=skills]').empty("");
                        if (skills.length >0)
                        { 
                            for (let i = 0; i < skills.length; i++) {
                             
                                    let skills_id = skills[i][0];
                                    let skills_name =  skills[i][1]  ;
                                    let option = $("<option>", {
                                        'value': Number(skills_id),
                                        'html': skills_name
                                    });
                                    $('select[name=skills]').append(option);
                                }
                        }
                        else
                        {
                            let option = $("<option>", {
                                        'value': 0,
                                        'html': "Aucun contenu disponible"
                                        });
                            $('select[name=skills]').append(option);
                        }

                    }
                }
            )
        }); 



        $('select[name=level]').on('change', function (event) {
            let level_id   = $(this).val();
            let subject_id = $("#id_subject").val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'level_id'  : level_id,
                        'subject_id': subject_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_theme_exercice",
                    success: function (data) {
                        $('select[name=theme]').html("");
                        // Remplir la liste des choix avec le résultat de l'appel Ajax
                        let themes = JSON.parse(data["themes"]);
                        for (let i = 0; i < themes.length; i++) {

                            let theme_id = themes[i].pk;
                            let name =  themes[i].fields['name'];
                            let option = $("<option>", {
                                'value': Number(theme_id),
                                'html': name
                            });

                            $('#id_theme').append(option);
                        }

                        $('select[name=knowledge]').html("");
                        // Remplir la liste des choix avec le résultat de l'appel Ajax
                        let knowledges = JSON.parse(data["knowledges"]);
                        for (let i = 0; i < knowledges.length; i++) {

                            let knowledge_id = knowledges[i].pk;
                            let name =  knowledges[i].fields['name'];
                            let option = $("<option>", {
                                'value': Number(knowledge_id),
                                'html': name
                            });

                            $('#id_knowledge').append(option);
                        }
                    }
                }
            )
        }); 
 
   
        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('select[name=theme]').on('change', function (event) {
            let theme_id = $(this).val();
            let level_id = $('select[name=level]').val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'theme_id': theme_id,
                        'level_id': level_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_knowledge_exercise",
                    success: function (data) {
                        $('select[name=knowledge]').html("");
                        // Remplir la liste des choix avec le résultat de l'appel Ajax
                        let knowledges = JSON.parse(data["knowledges"]);
                        for (let i = 0; i < knowledges.length; i++) {

                            let knowledge_id = knowledges[i].pk;
                            let name =  knowledges[i].fields['name'];
                            let option = $("<option>", {
                                'value': Number(knowledge_id),
                                'html': name
                            });

                            $('#id_knowledge').append(option);
                        }
                    }
                }
            )
        });

         $(document).on('change', 'select[name=knowledge]' , function (event) {

                k_value = $( "#id_knowledge option:selected" ).text(); 
                $("#id_title").val(k_value) ;

            });


         $(document).on('change', '.show_right_side' , function (event) {

                $("#right_side").toggle();
                $("#more_choice_button").toggle();
                $(".div_canvas").toggle();
                $(".maxi").toggle();
                $(".sup").toggle();
                $(".alert-sacado").toggle();
                $("#text_pseudo").toggle();
                $("#tr_pseudo").toggle();
                $("#tr_pseudo_sub").toggle();
                $("#situation_student").toggle();
                
                if ($("#left_side").hasClass("col-sm-12"))
                    {$("#left_side").removeClass("col-sm-12").addClass("col-sm-6");}
                else
                    {$("#left_side").removeClass("col-sm-6").addClass("col-sm-12");}


                $("#id_situation").val(5);


            });




 

        $(".setup_no_ggb").hide();
            makeItemAppear($("#id_is_ggbfile"), $(".setup_ggb"), $(".setup_no_ggb"));
            function makeItemAppear($toggle, $item, $itm) {
                    $toggle.change(function () {
                        if ($toggle.is(":checked")) {
                            $item.show(500);
                            $itm.hide(500);

                        } else {
                            $item.hide(500);
                            $itm.show(500);
                            }
                    });
                }


        $("#collaborative_div").hide();
            makeDivAppear($("#id_is_text"), $("#collaborative_div"));
            makeDivAppear($("#id_is_mark"), $("#on_mark"));
            makeDivAppear($("#id_is_autocorrection"), $("#positionnement"));

            function makeDivAppear($toggle, $item) {
                    $toggle.change(function () {
                        if ($toggle.is(":checked")) {
                            $item.show(500);

                        } else {
                            $item.hide(500);
                            }
                    });
                }

        // Cache les div
        $('.no_visu').hide();

         
        // Gère l'affichage de la div des notes.
        if ($("#id_is_mark").is(":checked")) {$("#on_mark").show();} else { $("#on_mark").hide(); } 
 
        function clickDivAppear(toggle, $item) {
            $(document).on('click', toggle , function () {
                        $(".no_display").hide();        
                        $item.toggle(500);
                });
            }
 

        $(document).on('click', "#show_latex_formula" , function () {
                    $(".no_display").hide();        
                    $("#latex_formula").toggle(500);

                if ( $('.proposition').hasClass('no_visu_on_load')  )
                {   
                    $('.proposition').removeClass('no_visu_on_load') ;
                    $('.reponse').addClass('col-md-5') ;
                    $('.reponse').removeClass('col-md-12') ;
                    $(".qr").html("").html("un couple Question/Réponse");
                }
                else
                {   
                    $('.proposition').addClass('no_visu_on_load') ;
                    $('.reponse').removeClass('col-md-5') ;
                    $('.reponse').addClass('col-md-12') ;
                    $(".qr").html("").html("une valeur de la variable");
                }
            });



        // ==================================================================================================
        // =========    Gestion de l'aléatoire et du pseudo aléatoire    ====================================
        // ==================================================================================================   

        var open_situation_randomize       = 0 ;
        var open_situation_pseudorandomize = 0 ;
        $("#new_item").hide() ;
        $('body').on('click', '#show_randomize_zone' , function (event) { 
            $('#randomize_zone').toggle(500);
            $('#alert_variable').toggle(500);
            $("#new_item").toggle(500) ;
            if (open_situation_randomize%2==0)  {
                $('#nb_situation').show(500);  
                $('#show_pseudorandomize_zone').attr('id','no_show_pseudorandomize_zone') ; 
                $('#no_show_pseudorandomize_zone').attr('disabled',true) ; 
                $('.add_more').attr('disabled',true) ;
                $('#show_randomize_zone').remove() ;
            }
            else {
                $('#nb_situation').hide(500);  
                $('#no_show_pseudorandomize_zone').attr('id','show_pseudorandomize_zone') ;
                $('#show_pseudorandomize_zone').attr('disabled',false) ;
                $('.add_more').attr('disabled',false) ;
            }
            open_situation_randomize +=1 ;

         });

        $('body').on('click', '#show_pseudorandomize_zone' , function (event) { 
            if (open_situation_pseudorandomize%2==0)
                {  
                    $('#nb_situation').show(500);
                    $('#show_randomize_zone').attr('id','no_show_randomize_zone') ; 
                    $('#no_show_randomize_zone').attr('disabled',true) ;  
                }
            else 
                {$('#nb_situation').hide(500);
                 $('#no_show_randomize_zone').attr('id','show_randomize_zone') ; 
                 $('#show_randomize_zone').attr('disabled',false) ;
             }
            open_situation_pseudorandomize +=1 ;
         });
        
        // ==================================================================================================
        // ==================================================================================================
        // ==================================================================================================





        $('#enable_correction_div').hide();
        $("#enable_correction").click(function(){ 
            $('#enable_correction_div').toggle(500);
        });

        $('#enable_correction').hide();
        $("#id_is_display_correction").on('change', function () { console.log("coucou");

            if ($("#id_is_display_correction").is(":checked")) { $("#enable_correction").show(500) ;}
            else { $("#enable_correction").hide(500) ;}
        });






        $("#id_is_python").on('change', function () { console.log("coucou");

            if ($("#id_is_python").is(":checked")) { $("#config_render").hide(500) ;}
            else { $("#config_render").show(500) ;}
        });


        $("#id_is_scratch").on('change', function () { console.log("coucou");

            if ($("#id_is_scratch").is(":checked")) { $("#config_render").hide(500) ;}
            else { $("#config_render").show(500) ;}
        });



        //*************************************************************************************************************
        //********      Gère le realtime         **********************************************************************
        //*************************************************************************************************************
        $("#id_is_realtime").on('change', function (){ 

            if ($(this).is(":checked")){
                $(".no_realtime").hide(500);
                $('#id_is_realtime').prop('checked', true); 
            } 
            else{

                $(".no_realtime").show(500);
                $('#id_is_realtime').prop('checked', false); 
            } 
        })


        //*************************************************************************************************************
        //*************************************************************************************************************
        //*************************************************************************************************************  

        $(document).on('click', '.add_more_question', function (event) { 

                var total_form = $('#id_variables-TOTAL_FORMS') ;
                var totalForms = parseInt(total_form.val())  ;

                var thisClone = $('#rowToClone_question');
                rowToClone = thisClone.html() ;

                $('#formsetZone_variables').append(rowToClone); 
                $('#duplicate_variables').attr("id","duplicate_variables"+totalForms) 

                $('#duplicate_variables'+totalForms).find('.delete_button_question').html('<a href="javascript:void(0)" class="btn btn-danger remove_more_question" ><i class="fa fa-trash"></i></a>'); 
                $('#duplicate_variables'+totalForms).find("input[type='checkbox']").bootstrapToggle();

                $("#duplicate_variables"+totalForms+" input").each(function(){ 
                    $(this).attr('id',$(this).attr('id').replace('__prefix__',totalForms));
                    $(this).attr('name',$(this).attr('name').replace('__prefix__',totalForms));
                });
                total_form.val(totalForms+1);

                $("#id_situation").val(5);

            });


        $(document).on('click', '.remove_more_question', function () {
            var total_form = $('#id_variables-TOTAL_FORMS') ;
            var totalForms = parseInt(total_form.val())-1  ;

            $('#duplicate_variables'+totalForms).remove();
            total_form.val(totalForms);

            if (totalForms==0) {$("#id_situation").val(1);}
        });
        //***********************************************************************************************
        //***********************************************************************************************
        //*************************************************************************************************************  
        // Gestion des thèmes
        //************************************************************************************************************* 

        $(document).on('click', '.add_more', function (event) {

                var supportchoices       = $('#id_supportchoices-TOTAL_FORMS') ;
                var total_supportchoices = parseInt( supportchoices.val() ) ;
                $("#nb_pseudo_aleatoire").html("").html(total_supportchoices+1);
                var thisClone = $('#rowToClone');
                rowToClone = thisClone.html() ;

                $('#formsetZone').append(rowToClone);
                $('#duplicate').attr("id","duplicate"+total_supportchoices) ;
                $('#cloningZone').attr("id","cloningZone"+total_supportchoices) ;
                $('#imager').attr("id","imager"+total_supportchoices) ;
                $('#file-image').attr("id","file-image"+total_supportchoices) ;
                $('#feed_back').attr("id","feed_back"+total_supportchoices)  ;       
                $('#div_feed_back').attr("id","div_feed_back"+total_supportchoices)  ;
                $('#delete_img').attr("id","delete_img"+total_supportchoices)  ;
                $('#data_loop').attr("data-loop", total_supportchoices)  ;
                $('#data_loop').attr("id","data_loop"+total_supportchoices)  ;

                if( $('#imagerbis').length ) { 
                    $('#imagerbis').attr("id","imagerbis"+total_supportchoices) ; 
                    $('#file-imagebis').attr("id","file-imagebis"+total_supportchoices) ;
                    $('#preview_bis').attr("id","preview_bis"+total_supportchoices) ;
                    $('#delete_imgbis').attr("id","delete_imgbis"+total_supportchoices)  ;
                } 
                $('#subformsetZone').attr("id","subformsetZone"+total_supportchoices)  ;


                $('#canvas').attr("data-loop",total_supportchoices )  ;
                $('#canvas').attr("id", $('#canvas').attr("id")+total_supportchoices )  ;
                $('#div_canvas').attr("id", $('#div_canvas').attr("id")+total_supportchoices )  ;

                if ( $('#imagersub').length > 0 ) { 

                    l_items = $("#subformsetZone"+total_supportchoices+" .get_image").length ; 
                    for(var i = 0;i<l_items;i++ ){
                        var suf = "-"+total_supportchoices+'_'+i ; 
                        $('#imagersub').attr("id","imagersub"+suf) ;
                        $('#file-imagesub').attr("id","file-imagesub"+suf) ;
                        $('#previewsub').attr("id","previewsub"+suf) ;
                        $('#delete_subimg').attr("id","delete_subimg"+suf)  ;
                    }

                    this_selector = $("#subformsetZone"+total_supportchoices+" input"); 
                    new_attr_id = this_selector.attr("id")+suf  ;
                    new_attr_nm = this_selector.attr("name")+suf  ;
                    this_selector.attr("data-loop",suf);                        
                    this_selector.attr("id",new_attr_id);
                    this_selector.attr("name",new_attr_nm);

                    this_answer = $("#subformsetZone"+total_supportchoices+" textarea"); 
                    new_attr_id = this_answer.attr("id")+suf  ;
                    new_attr_nm = this_answer.attr("name")+suf  ;
                    this_answer.attr("data-loop",suf);                        
                    this_answer.attr("id",new_attr_id);
                    this_answer.attr("name",new_attr_nm);
                } 
                
                $("#id_supportchoices-"+total_supportchoices+"-is_correct").prop("checked", false); 
                $("#id_supportchoices-"+total_supportchoices+"-is_written").prop("checked", false); 

                $("#duplicate"+total_supportchoices+" input").each(function(index){
                    $(this).attr('id',    $(this).attr('id').replace('__prefix__',total_supportchoices)    );
                    $(this).attr('name',  $(this).attr('name').replace('__prefix__',total_supportchoices)   );
                });

                $('#duplicate'+total_supportchoices).find("input[type='checkbox']").bootstrapToggle();
 
                $("#duplicate"+total_supportchoices+" textarea").each(function(){ 
                    $(this).attr('id',$(this).attr('id').replace('__prefix__',total_supportchoices));
                    $(this).attr('name',$(this).attr('name').replace('__prefix__',total_supportchoices));
                });
 

                $('#spanner').attr("id","spanner"+total_supportchoices) ;
                $('#preview').attr("id","preview"+total_supportchoices) ;

                $('#loop'+total_supportchoices).val(total_supportchoices) ;
                $('#subloop'+total_supportchoices).val(0) ;

                $('#subformsetZone'+total_supportchoices).append('<input type="hidden" name="supportchoice-supportchoices-'+total_supportchoices+'-subchoice-TOTAL_FORMS" value="0" id="id_supportchoice-supportchoices-'+total_supportchoices+'-subchoice-TOTAL_FORMS">');
                $('#subformsetZone'+total_supportchoices).append('<input type="hidden" name="supportchoice-supportchoices-'+total_supportchoices+'-subchoice-INITIAL_FORMS" value="0" id="id_supportchoice-supportchoices-'+total_supportchoices+'-subchoice-INITIAL_FORMS">');
                $('#subformsetZone'+total_supportchoices).append('<input type="hidden" name="supportchoice-supportchoices-'+total_supportchoices+'-subchoice-MIN_NUM_FORMS" value="0" id="id_supportchoice-supportchoices-'+total_supportchoices+'-subchoice-MIN_NUM_FORMS">');
                $('#subformsetZone'+total_supportchoices).append('<input type="hidden" name="supportchoice-supportchoices-'+total_supportchoices+'-subchoice-MAX_NUM_FORMS" value="1000" id="id_supportchoice-supportchoices-'+total_supportchoices+'-subchoice-MAX_NUM_FORMS">');


                var this_step = parseInt(total_supportchoices)-1;
                $('#principal'+this_step).addClass('answer_box_active') ;

                supportchoices.val(total_supportchoices+1);
            });



        $(document).on('click', '.remove_more', function () {
            
            var supportchoices = $('#id_supportchoices-TOTAL_FORMS') ;
            var total_supportchoices = parseInt( supportchoices.val() )-1  ;

            var this_step = parseInt(total_supportchoices)-1;
            $('#principal'+this_step).removeClass('answer_box_active') ;


            $('#duplicate'+total_supportchoices).remove();
            supportchoices.val(total_supportchoices);
            $("#nb_pseudo_aleatoire").html("").html(total_supportchoices);
        });


        //*************************************************************************************************************  
        // Gestion des images des thèmes
        //************************************************************************************************************* 

        $('body').on('change', '.choose_imageanswer' , function (event) {

            var nb = this.id.match(/\d+/);  
            const file = $('#id_supportchoices-'+nb+'-imageanswer')[0].files[0];
            const reader = new FileReader();
            $("#file-image"+nb).addClass("preview") ;
            $("#div_canvas"+nb).append('<a href="javascript:void()" id="delete_img'+nb+'" class="btn btn-danger delete_img">Supprimer cette image</a>');
            reader.addEventListener("load", function (e) {
                                                var image = e.target.result ; 
                                                $("#canvas"+nb).css("background-image", "url(" + image + ")"  );
                                                $("#canvas"+nb).attr('width',image.width+"px"); 
                                                $("#canvas"+nb).attr('height',image.height+"px");
                                            }) ;
            if (file) { reader.readAsDataURL(file);} 







         });  


        $('body').on('click', '.delete_img' , function (event) { 
                var nb = this.id.match(/\d+/); 
                $("#id_supportchoices-"+nb+"-imageanswer").val('');
                $("#file-image"+nb).removeClass("preview") ;
                $("#preview"+nb).addClass("preview") ; 
                $("#id_supportchoices"+nb+"-imageanswer").removeClass("preview") ;
                $("#canvas"+nb).css("background-image", "" );
                $(this).remove(); 

            });  



        //*************************************************************************************************************  
        // Gestion des sous thèmes
        //************************************************************************************************************* 


        $(document).on('click', '.add_sub_more', function (event) { 

                loop = $(this).attr("data-loop"); 
                this_id = $("#id_supportchoice-supportchoices-"+loop+"-subchoice-TOTAL_FORMS");
                var ntotal_form = this_id.val()
                var ntotalForms = parseInt(ntotal_form )  ;

                subToClone = $('#subToClone').html() ;

                $('#subformsetZone'+loop).append(subToClone);

                var subloop  = $('#subloop'+loop).val();
                var new_prefix = "supportchoice-supportchoices-"+loop+"-subchoice-"+subloop;

                $("#subformsetZone"+loop+" input").each(function(){                  
                    $(this).attr('id',$(this).attr('id').replace('supportchoice-supportchoices-0-subchoice-__prefix__', new_prefix ));  

                    $(this).attr('name', $(this).attr('name').replace('supportchoice-supportchoices-0-subchoice-__prefix__',new_prefix) );

                });

                $("#subformsetZone"+loop+" textarea").each(function(){ 
                    $(this).attr('id',$(this).attr('id').replace('supportchoice-supportchoices-0-subchoice-__prefix__', new_prefix ));  

                    $(this).attr('name', $(this).attr('name').replace('supportchoice-supportchoices-0-subchoice-__prefix__',new_prefix) );
                });

                $("#subformsetZone"+loop+" span").attr('data-loop', loop);

                for (var i=0;i<9;i++){

                    classes = ['danger','warning','rose','white','light','success','info','navy','muted'];

                    let selector = $("#this_"+classes[i]);
                    selector.addClass('this_subloop'+subloop);
                    selector.attr('data-loop',loop);
                    selector.attr('data-subloop',subloop);
                    selector.attr('id',  selector.attr('id')+"-"+loop+"-"+subloop  )
                }

                var subloop_int = parseInt( subloop )  ;  
                $('#subloop'+loop).val( subloop_int + 1 );  
                this_id.val( ntotalForms+ 1 );
            });



        $(document).on('click', '.remove_sub_more', function () {
 
            loop = $(this).attr("data-loop");
            subloop = $('#subloop'+loop).val();
            var subloop_int = parseInt( subloop )  ;  
            $('#subloop'+loop).val( subloop_int - 1 );  
            this_id = $("#id_supportchoice-supportchoices-"+loop+"-subchoice-TOTAL_FORMS");
            this_id.val( subloop_int - 1 );
            $(this).parent().parent().parent().remove();
            $("#div_canvas"+loop).children()[subloop_int-1].remove();

        });

 


        //*************************************************************************************************************  
        // Gestion des images des sous thèmes
        //*************************************************************************************************************  
        $('body').on('change', '.to-data-loop' , function (event) { 
            
            const parental_div     = $(this).parent();
            const image_preview_id = parental_div.find('img').attr('id');
            const file  = parental_div.find('input')[0].files[0];
            const reader = new FileReader();

            parental_div.find('svg').addClass('preview');
            parental_div.next().append('<a href="javascript:void()" class="delete_subimg"><i class="fa fa-trash"></i></a>');

            $("#"+image_preview_id).removeClass('preview');
            reader.addEventListener("load", function (e) {
                                                var image = e.target.result ; 
                                                $("#"+image_preview_id).attr("src", image );
                                            }) ;
            if (file) { reader.readAsDataURL(file);}            
         });  


        $('body').on('click', '.delete_subimg' , function (event) { 

            const parental_div = $(this).parent().parent() ;

            parental_div.find('input').val("");
            parental_div.find('img').attr("src", "" );
            parental_div.find('img').addClass('preview');
            parental_div.find('svg').removeClass('preview');
            $(this).remove();
            }); 


        //*************************************************************************************************************  
        // FIN DE gestion
        //************************************************************************************************************* 






        // Chargement d'une image dans la réponse possible.
        $('body').on('click', '.automatic_insertion' , function (event) {  
 
            var feed_back = $(this).attr('id');
            $("#div_"+feed_back).toggle(500);

         });


        // Supprimer une image réponse depuis la vue élève.
        $('.delete_custom_answer_image').on('click', function () {

            let image_id = $(this).attr("data-image_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let custom = $(this).attr("data-custom");

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'image_id': image_id,
                        'custom' : custom,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_delete_custom_answer_image",
                    success: function (data) {

                        $("#delete_custom_answer_image"+image_id).remove();
                    }
                }
            )
         });

 
        // Supprimer une image réponse depuis la vue élève.
        $('body').on('click', '#click_more_criterion_button' , function () {

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            let label=$("#id_label").val() ;
            let skill= $("#id_skill").val() ;
            let knowledge = $("#id_knowledge").val() ;
            let subject = $("#id_subject").val() ;
            let level = $("#id_level").val() ;

 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'label': label,
                        'skill': skill,
                        'knowledge': knowledge,
                        'subject': subject,
                        'level' : level,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_add_criterion",
                    success: function (data) {
 
 

                        criterions = data["criterions"] ; 
                        $('#id_criterions').empty("");

                        for (let i = 0; i < criterions.length ; i++) {
                                    
                                let criterions_id = criterions[i][0]; 
                                let criterions_name =  criterions[i][1] ; 
 
                                $('#id_criterions').append('<label for="id_criterions_'+Number(criterions_id)+'"><input type="checkbox" id="id_criterions_'+Number(criterions_id)+'" name="criterions" value="'+Number(criterions_id)+'" /> '+criterions_name+'</label><br/>')
                            }

                    }
 
                }
            )
         });


////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////
///// Gestion de l'axepour qtype = 18.
////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////

        $(document).on('focusout',".axe_creator", function (event) { 
            let index = $(this).parent().parent().children()[0].value ;
            var canvas = document.getElementById("canvas"+index);
            var ctx = canvas.getContext("2d");
            ctx.beginPath();
            // Tracé de l'axe
            ctx.moveTo(25,60);
            ctx.lineTo(625,60);   
            //graduation
            ctx.font = '25px Arial';
            origin  = $(this).val();
            ctx.clearRect(15, 15, 35, 35);
            ctx.fillText( origin, 18, 45); 
            ctx.moveTo(25,50); // haut de la graduation
            ctx.lineTo(25,70); // bas de la graduation
            ctx.stroke();
            ctx.closePath();
         });

        $(document).on('focusout',".axe_extremite", function (event) { 
            let index = $(this).parent().parent().children()[0].value ;
            var canvas = document.getElementById("canvas"+index);
            var ctx = canvas.getContext("2d");
            ctx.beginPath();
            ctx.font = '25px Arial';
            detail  = $(this).val();
            ctx.clearRect(600, 15, 60, 35);
            ctx.fillText( detail, 610, 45);    
            ctx.moveTo(625,50); // haut de la graduation
            ctx.lineTo(625,70); // bas de la graduation
            ctx.stroke();
            ctx.closePath();
         });


        $(document).on('focusout',".axe_tick", function (event) {  // tick
            var loop = $(this).parent().parent().children()[0].value ;
            var tick = $(this).val();
            var xmin =  $("#id_supportchoices-"+loop+"-xmin").val();
            var xmax =  $("#id_supportchoices-"+loop+"-xmax").val();
            var canvas = document.getElementById("canvas"+loop);
            var ctx = canvas.getContext("2d");
            if ((xmin=="") || (xmax=="")) { alert('Renseignez xmin et xmax.') ; return false ;}
            ctx.beginPath();
            ctx.moveTo(25,55); // haut de la graduation
            ctx.lineTo(25,65); // bas de la graduation
            var a  = 25;
            var step = 600/( (xmax - xmin)/tick ) ;
            while (a<625){
                a = a + step;
                ctx.moveTo(a,50);
                ctx.lineTo(a,70);
            }
            ctx.stroke();
            ctx.closePath();   
         });


        $(document).on('focusout',".axe_subtick", function (event) { // subtick

            var loop = $(this).parent().parent().children()[0].value ;
            var tick = $(this).val();
            var xmin =  $("#id_supportchoices-"+loop+"-xmin").val();
            var xmax =  $("#id_supportchoices-"+loop+"-xmax").val();
            var canvas = document.getElementById("canvas"+loop);
            var ctx = canvas.getContext("2d");
            if ((xmin=="") || (xmax=="")) 
                { alert('Renseignez xmin et xmax.') ; 
                if (xmin=="") { $("#id_supportchoices-"+loop+"-xmin").focus() ; } else { $("#id_supportchoices-"+loop+"-xmax").focus() ; }
            return false ;
            }
            ctx.beginPath();
            ctx.moveTo(25,55); // haut de la graduation
            ctx.lineTo(25,65); // bas de la graduation
            var a  = 25;
            var step = 600/tick/ (xmax - xmin) ;
            while (a<625){
                a = a + step;
                ctx.moveTo(a,55);
                ctx.lineTo(a,65);
            }
            ctx.stroke();
            ctx.closePath();   
         });

         $(document).on('click',".eraser", function (event) { // subtick

            var loop = $(this).data("loop") ;
            $("#id_supportchoices-"+loop+"-xmin").val("");
            $("#id_supportchoices-"+loop+"-xmax").val("");
            $("#id_supportchoices-"+loop+"-tick").val("");
            $("#id_supportchoices-"+loop+"-subtick").val("");
            var canvas = document.getElementById("canvas"+loop);
            var ctx = canvas.getContext("2d");
            ctx.clearRect(5, 5, 650, 75);
         });


////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////
///// Couleurs des markers
////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////

        var classi = 0 ;
        $('body').on('click', '.get_color' , function (event) {  
 
            let loop = $(this).data('loop');
            let subloop = $(this).data('subloop');
            let classe = $(this).data('classe');            
            let suffixe = loop+"-"+subloop;
            let subloop_selector = $('.this_subloop'+loop).find('i')

            subloop_selector.removeClass('fa-2x').removeClass('this_marker');
            $(this).find('i').addClass('fa-2x').addClass('this_marker');

            let parent = $(this).parent().parent().parent().parent();
            let old_border = parent.attr('data-classe');
            parent.removeClass(old_border);
            parent.addClass('border-'+classe);
            parent.attr('data-classe','border-'+classe);
            
            $('.get_color').removeClass('this_marker_selected');
            $(this).addClass('this_marker_selected');

         });

 

////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////   Créer le marker
////////////////////////////////////////////////////////////////////////////////////////////////////////////
 
        $(document).on('click', '.image_canvas', function (e) {  

            let selector    = $(".this_marker_selected");
            let loop        = selector.data('loop'); 
            let subloop     = selector.data('subloop');                      
            let this_classe = selector.data("classe") ; 


            if ( selector.length)
            { place_marker( e, this_classe ,loop , subloop ) ; }

        });

////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////   Supprime la div cliquée
////////////////////////////////////////////////////////////////////////////////////////////////////////////
         $(document).on('click', '.remove', function () {
                original_id = $(this).data("original_id") ;
                o_tab =  original_id.split("-");
                $(this).parent().remove();
                $("#this_"+original_id).addClass('get_color');
                $(".this_subloop"+o_tab[2]).addClass('get_color');
                $("#this_"+original_id).find('i').removeClass('fa-2x');
                $("#this_"+original_id).parent().parent().parent().parent().removeClass('border-'+o_tab[0]);
            });

////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////      Création des annontations  
////////////////////////////////////////////////////////////////////////////////////////////////////////////

        function place_marker(event,this_classe,loop,subloop){ 


                    // décale l'abscisse selon la position du clic de la souris
                    let abscisse = event.offsetX; // - 412
                    
                    // décale l'ordonnée selon la hauteur du clic de la souris
                    let ordonnee = event.offsetY - 25   ; //  - 82
                    
                    //////////////////////////////////////
                    ////// Création des annotations //////
                    //////////////////////////////////////
                    let marker = "<i class='fa fa-map-marker fa-2x text-"+this_classe+"' data-classe="+this_classe+"></i>" ;
                    
                    // Poubelle Effaceur
                    let original_id = this_classe+"-"+loop+"-"+subloop;
                    marker = marker+"<a href='javascript:void();' class='pull-right gray remove' data-original_id='"+original_id+"''><i class='fa fa-times' style='font-size:9px'></i></a>";
                    
                    // La div crée dans le HTML et son style
                    let style = "position:absolute;left:"+abscisse+"px; top:"+ordonnee+"px;z-index:99;" ;
                    
                    let myDiv = "<div class='marker_draggable' style='"+style+"'>"+marker+"</div>";

                    // Ajout de myDiv à la div via son id  
                    $('#div_canvas'+loop).append(myDiv) ;

                    console.log('#div_canvas'+loop);

                    // Rend la nouvelle div draggable
                    $(".marker_draggable").draggable();

                    // Supprime l'activation du marker 
                    $("#this_"+original_id).removeClass('get_color').removeClass('this_marker_selected');
                    $("#subformsetZone"+loop+" .this_subloop"+subloop).removeClass('get_color');

                    $("#id_supportchoice-supportchoices-"+loop+"-subchoice-"+subloop+"-answer").val(this_classe+"|"+abscisse+"|"+ordonnee);
                  } 

////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////// Déplace le marker
////////////////////////////////////////////////////////////////////////////////////////////////////////////

        $( ".marker_draggable " ).draggable({
                        classes: {
                          "ui-draggable": "move"
                        }
                      });  
        // Permet de déplacer une annotation après son enregistrement dans la base de donnée
        $( document ).on('mouseup', ".marker_draggable " , function(event){ 

            original_id = $(this).find("a").data("original_id") ;
            o_tab =  original_id.split("-");

            let style = $(this).attr('style');
            let s_tab = style.split(';')
            let left = s_tab[1]; 
            let abscisse = left.match(/\d+/);
            let top  = s_tab[2];
            let ordonnee =top.match(/\d+/) ;
            $("#id_supportchoice-supportchoices-"+o_tab[1]+"-subchoice-"+o_tab[2]+"-answer").val(o_tab[0]+"|"+abscisse+"|"+ordonnee);

        }); 


 

});

});

 
