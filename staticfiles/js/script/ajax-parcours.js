define(['jquery','bootstrap'], function ($) {
    $(document).ready(function () {

        console.log("chargement JS ajax-parcours.js OK");

        $(".is_evaluation").attr("checked",false);

        // ================================================================ 
        // Parcours menu vertical pour les cours
        var navItems = $('.admin-menu li > a');
        var navListItems = $('.admin-menu li');
        var allWells = $('.admin-content');
        var allWellsExceptFirst = $('.admin-content:not(:first)');
        allWellsExceptFirst.hide();
        navItems.click(function(e)
        {
            e.preventDefault();
            navListItems.removeClass('active');
            $(this).closest('li').addClass('active');
            
            allWells.hide();
            var target = $(this).attr('data-target-id');
            $('#' + target).show();
        });
        // ================================ FIN ============================ 

        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('#id_level').on('change', function (event) {
            let id_level = $(this).val();
            let is_update = $("#is_update").val();
            if ((id_level == "")||(id_level == " ")) { alert("Sélectionner un niveau") ; return false ;}
            let id_subject = $("#id_subject").val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            if (is_update=="1") {
                    url_ = "../../../ajax/chargethemes" ;
            } 
            else {
                    url_ = "../../ajax/chargethemes" ;
            }



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
                    url : url_,
                    success: function (data) {

                        themes = data["themes"] ; 
                        $('select[name=theme]').empty("");



                        if (data.imagefiles) { 

                                    $('#label_vignette').html("").html("<label>Proposition de vignettes - cliquer pour sélectionner</label>");

                                    $('#prop_vignette').html("");
                                    imgs = "";
                                    for (let i = 0; i < data.imagefiles.length; i++) {
                                 
                                                    imgs = imgs + "<img src='https://sacado-academie.fr/ressources/"+data.imagefiles[i]+"'  width='200px'  data-url_image='"+data.imagefiles[i]+"' class='selector_image_from_ajax' />";
                                                }
                                            
                                            $('#prop_vignette').append(imgs);

                                        }



                        if (themes.length >0)
                        { for (let i = 0; i < themes.length; i++) {
                                    
                                    let themes_id = themes[i][0];
                                    let themes_name =  themes[i][1]  ;
                                    let option = $("<option>", {
                                        'value': Number(themes_id),
                                        'html': themes_name
                                    });
                                    $('select[name=theme]').append(option);
                                }
                        }
                        else
                        {
                                    let option = $("<option>", {
                                        'value': 0,
                                        'html': "Aucun contenu disponible"
                                    });
                            $('select[name=theme]').append(option);
                        }


                    }
                }
            )
        });
 

  // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('#level_id').on('change', function (event) {

            let id_level = $(this).val();
            if (id_level == " ") { alert("Sélectionner un niveau") ; return false ;}

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
                    url : "../ajax/chargethemes_parcours",
                    success: function (data) {

                        themes = data["themes"];
                        $('select[name=theme]').empty("");
                        if (themes.length >0)

                        { for (let i = 0; i < themes.length; i++) {
                                    

                                    console.log(themes[i]);
                                    let themes_id = themes[i][0];
                                    let themes_name =  themes[i][1]  ;
                                    let option = $("<option>", {
                                        'value': Number(themes_id),
                                        'html': themes_name
                                    });
                                    $('select[name=theme]').append(option);
                                }
                        }
                        else
                        {
                                    let option = $("<option>", {
                                        'value': 0,
                                        'html': "Aucun contenu disponible"
                                    });
                            $('select[name=theme]').append(option);
                        }


                        $('#parcours_details').html("").html(data.html);

                        $("#loading").hide(500); 
                    }
                }
            )
        });

        $('#thm_id').on('change', function (event) { 
 
            if (  $('select[name=level]').val() > 0 )
            {
                    let level_id = $('#level_id').val();
                    if (level_id == " ") { alert("Sélectionner un niveau") ; return false ;}
                    let theme_id = $(this).val();
                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                    $("#loader").html("<i class='fa fa-spinner fa-pulse fa-3x fa-fw'></i>");
                                
                    $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            traditional: true,
                            data: {
                                'level_id': level_id,
                                'theme_id': theme_id,
                                csrfmiddlewaretoken: csrf_token
                            },
                            url: '../ajax_all_parcourses',
                            success: function (data) {
         
                                $('#parcours_details').html("").html(data.html);
                                $("#loader").html("").hide(); 
                                
                                }
                        }
                    )
          
            }
            else 
            {   
                alert("Vous devez choisir un niveau."); return false;             
            }
        }); 

  // récupère l'url de l'image dans le form d'un parcours pour l'utiliser dans la base de données
        $('body').on('click', '.selector_image_from_ajax' , function () {

                let url_image = $(this).data("url_image");

                console.log(url_image) ;
                $('#this_image_selected').val(url_image);

                $('.selector_image_from_ajax').addClass('opacity_selector_img');  
                $(this).removeClass('opacity_selector_img'); 

            });





        $('#id_theme').on('change', function (event) {

            if (  $('select[name=level]').val() > 0 )
            {
                ajax_choice($('select[name=level]'),$('select[name=theme]')) ;            
            }
            else 
            {   
                alert("Vous devez choisir un niveau."); return false;             
            }
        }); 

        $('.send_message').on('click', function () {

            let name = $(this).attr("data-student_name"); 
            let email = $(this).attr("data-student_email"); 
 
            $('#email').val(email);
            $('#name').val(name);
 
            });


        function ajax_choice(param0, param1){

            let is_parcours = $("#is_parcours").val();
            let level_id = param0.val();
            let theme_id = param1.val();

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            if ( is_parcours == "1" ) 
                { 
                    url= "../../ajax_level_exercise" ; 
                } 
            else 
                { 
                    url = "ajax_level_exercise";
                }

            var parcours_id = $("#id_parcours").val();

            if($("#loader")) {$("#loader").html("<i class='fa fa-spinner fa-pulse fa-3x fa-fw'></i>");      }

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional: true,
                    data: {
                        'parcours_id': parcours_id ,
                        'level_id': level_id,
                        'theme_id': theme_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: url,
                    success: function (data) {
 
                        $('#content_exercises').html("").html(data.html);
                        $("#loader").html(""); 
                        
                        }
                }
            )

        }



        $('.select_all').on('change', function (event) {

            var valeurs = [];
            $(".select_all").each(function() {

                if ($(this).is(":checked"))

                        {   let group_id = $(this).val(); 
                            if (group_id !="")
                                {valeurs.push(group_id);}
                        }

            });

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            url_ = "../../ajax_charge_folders" ;

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional: true,
                    data: {
                        'group_ids': valeurs,                       
                        csrfmiddlewaretoken: csrf_token
                    },
                    url : url_,
                    success: function (data) {

                        folders = data["folders"] ; 
                        $('#cblist').empty("");

                        if (folders.length >0)
                        { for (let i = 0; i < folders.length ; i++) {
                                    
                                    let folders_id = folders[i][0]; 
                                    let folders_name =  folders[i][1] ; 
 
                                    $('#cblist').append('<label for="cb'+Number(folders_id)+'"><input type="checkbox" id="cb'+Number(folders_id)+'" name="folders" value="'+Number(folders_id)+'" /> '+folders_name+'</label><br/>')
                                }
                        }
 
                    }
                }
            )
        });






        $(".subparcours_show_close").click(function(){
            value =  $(this).data("close"); 
            name =  $(this).data("name"); 
            $('#'+name+value).toggle(500);
        });

        $(".collapser").click(function(){
            value =  $(this).data("group"); 
            $('.collapside'+value).toggle(500);
        });
        
        // Affiche div_results dans le parcours_show_student des élèves
        $('.div_results').hide();
        $('.div_results_custom').hide();

        $(".selector_div_result_custom").click(function(){
            value =  $(this).data("customexercise_id"); 
            $('#div_results_custom'+value).toggle(500);
        });

        $(".div_results_custom_close").click(function(){
            value =  $(this).data("customexercise_id"); 
            $('#div_results_custom'+value).toggle(500);
        });



        $(".selector_div_result").click(function(){
            value =  $(this).data("relation_id");
            $('#div_results'+value).toggle(500);
        });

        $(".div_results_close").click(function(){
            value =  $(this).data("relation_id"); 
            $('#div_results'+value).toggle(500);
        });


        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.menuactionparcours').on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let is_disabled = $(this).attr("data-is_disabled");

            console.log(is_disabled) ;

            if (is_disabled == "0"){ $('#remove_student').prop('disabled', false); } else { $('#remove_student').prop('disabled', true) ; }

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../../group/ajax/chargelistgroup",
                    success: function (data) {
                        $('#parcours_id').val(parcours_id);
                        $('#modal_group_name').html(data.html_modal_group_name);
                        $('#list_students').html(data.html_list_students);
                    }
                }
            )
        });


        // Met en favori un parcours
        $('.selector_favorite').on('click' ,function () {
            let target_id = $(this).attr("data-target_id"); 
            let statut = $(this).attr("data-fav"); 
            let status = $(this).attr("data-status"); 

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'target_id': target_id,
                        'statut': statut,
                        'status': status,

                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "ajax_is_favorite",
                    success: function (data) {
                        $('#is_favorite_id'+target_id).html(data.statut);
                        $('#selector_favorite'+target_id).attr("data-fav",data.fav);      
                    }
                }
            )
        });



 
        $('body').on('click' , '.selector_e', function () {

            let parcours_id = $(this).attr("data-parcours_id"); 
            let exercise_id = $(this).attr("data-exercise_id"); 
            let statut = $(this).attr("data-statut"); 

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'parcours_id': parcours_id,
                        'exercise_id': exercise_id,
                        'statut': statut,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_populate",
                    success: function (data) {
                        $('#is_selected'+exercise_id).html(data.html);   
                        $('#selector_e'+exercise_id).attr("data-statut",data.statut);                  
                        $('#selector_e'+exercise_id).removeClass(data.noclass);
                        $('#selector_e'+exercise_id).addClass(data.class);
                        $('#nb_exercises').html("").html(data.nb+" exercice.s");     
                    }
                }
            )
        });

        // ===============================================================
        // ===============================================================
        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('body').on('click' , '.select_student', function () {

            let parcours_id = $(this).attr("data-parcours_id"); 
            let exercise_id = $(this).attr("data-exercise_id"); 
            let statut = $(this).attr("data-statut"); 
            let custom = $(this).attr("data-custom"); 
            let student_id = $(this).attr("data-student_id");

            let is_checked = false ;
            if ($("#select_all_exercices").val()) { 
                is_checked = $("#select_all_exercices").is(":checked") ;
            }
            
 


            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            
            if (student_id != 0)
            {  
                if (statut == "True") {
                    if (!confirm('Vous souhaitez dissocier un élève à un exercice ?')) return false;                    
                }
            }
            else
            {    
                if (!confirm("Vous souhaitez modifier l'association de cet exercice à tout votre groupe ?")) return false;
            }


            if (custom == "1"){
                $("#loadingCustom"+exercise_id).html("<i class='fa fa-spinner fa-pulse fa-3x fa-fw'></i>"); 
            } else {
                $("#loading"+exercise_id).html("<i class='fa fa-spinner fa-pulse fa-3x fa-fw'></i>"); 
            }



            $.ajax( 
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'parcours_id': parcours_id,
                        'exercise_id': exercise_id,
                        'student_id': student_id,
                        'statut': statut,
                        'custom': custom,
                        'is_checked' : is_checked ,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_individualise",
                    success: function (data) {

 

                    if (is_checked)
                        {
 
                            if (custom == "1"){

                                if (student_id == 0)
                                    {       
    
                                    $('.select_student' ).attr("data-statut",data.statut);                  
                                    $('.select_student' ).removeClass(data.noclass);
                                    $('.select_student' ).addClass(data.class);
                                    }
                                else 
                                    {  
 
                                    $('.selected_studentCustomExo'+student_id).attr("data-statut",data.statut);                  
                                    $('.selected_studentCustomExo'+student_id).removeClass(data.noclass);
                                    $('.selected_studentCustomExo'+student_id).addClass(data.class);                        
                                    }

                                $("#loadingCustom"+exercise_id).html("");  
                                $('#selecteurCustom'+exercise_id).attr("data-statut",data.statut);   

                            }
                            else{ 
 
                                if (student_id == 0)
                                    {  
 
                                    $('.select_student' ).attr("data-statut",data.statut);                  
                                    $('.select_student' ).removeClass(data.noclass);
                                    $('.select_student' ).addClass(data.class);
                                    }
                                else 
                                    { 
                                    $('.selected_studentExo'+student_id).html(data.html);   
                                    $('.selected_studentExo'+student_id).attr("data-statut",data.statut);                  
                                    $('.selected_studentExo'+student_id).removeClass(data.noclass);
                                    $('.selected_studentExo'+student_id).addClass(data.class);                      
                                    }

                                if (data.indiv_hide) 
                                    { $('#individialise_id_student'+exercise_id).removeClass("checkbox_no_display");
                                      $('#nb_indiv_id_student'+exercise_id).html("").html(data.indiv_nb);
                                    }
                                else{
                                    { $('#individialise_id_student'+exercise_id).addClass("checkbox_no_display");}
                                }

                                $("#loading"+exercise_id).html("");  
                                $('#selecteur'+exercise_id).attr("data-statut",data.statut);    

                            }

                        }

                    else
                        {

                            if (custom == "1"){

                                if (student_id != 0)
                                    {       
 
                                    $('#studentCustom'+exercise_id+"-"+student_id).attr("data-statut",data.statut);                  
                                    $('#studentCustom'+exercise_id+"-"+student_id).removeClass(data.noclass);
                                    $('#studentCustom'+exercise_id+"-"+student_id).addClass(data.class);
                                    }
                                else 
                                    { 
 
                                    $('.selected_studentCustom'+exercise_id).attr("data-statut",data.statut);                  
                                    $('.selected_studentCustom'+exercise_id).removeClass(data.noclass);
                                    $('.selected_studentCustom'+exercise_id).addClass(data.class);                        
                                    }

                                $("#loadingCustom"+exercise_id).html("");  
                                $('#selecteurCustom'+exercise_id).attr("data-statut",data.statut);   

                            }
                            else{ 

                                if (student_id != 0)
                                    {       
 
                                    $('#student'+exercise_id+"-"+student_id).attr("data-statut",data.statut);                  
                                    $('#student'+exercise_id+"-"+student_id).removeClass(data.noclass);
                                    $('#student'+exercise_id+"-"+student_id).addClass(data.class);
                                    }
                                else 
                                    { 
   
                                    $('.selected_student'+exercise_id).attr("data-statut",data.statut);                  
                                    $('.selected_student'+exercise_id).removeClass(data.noclass);
                                    $('.selected_student'+exercise_id).addClass(data.class);                      
                                    }

                                if (data.indiv_hide) 
                                    { 
                                        $('#individialise_id_student'+exercise_id).removeClass("checkbox_no_display");
                                        $('#nb_indiv_id_student'+exercise_id).html("").html(data.indiv_nb); 
                                    }
                                else{
                                    { $('#individialise_id_student'+exercise_id).addClass("checkbox_no_display");}
                                }

                                $("#loading"+exercise_id).html("");  
                                $('#selecteur'+exercise_id).attr("data-statut",data.statut);    

                            }

                        }


                    if (data.alert){ alert("Certains exercices ont fait l'objet d'une réponse par certains élèves. Vous ne pouvez plus les dissocier.");}

                    }
                }
            )
        });



        $('body').on('click' , '.reseted_student', function () {

            let parcours_id = $(this).attr("data-parcours_id");
            let exercise_id = $(this).attr("data-exercise_id");
            let student_id  = $(this).attr("data-student_id");
            let csrf_token  = $("input[name='csrfmiddlewaretoken']").val();
            
            if (student_id != 0)
            {  
                if (!confirm('Vous souhaitez effacer les résultats pour cet élève  ?')) return false;                    
            }
            else
            {    
                if (!confirm("Vous souhaitez effacer les résultats pour  tout votre groupe ?")) return false;
            }


            $.ajax( 
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'parcours_id': parcours_id,
                        'exercise_id': exercise_id,
                        'student_id' : student_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../ajax_reset",
                    success: function (data) {

                        if (student_id != 0)
                            {       
                                $('#check_reseted_student'+student_id).html("<i class='fa fa-check text-success'></i>");                 
                            }
                        else 
                            { 
                                $('.check_reseted_student').html("<i class='fa fa-check text-success'></i>");                        
                            }
                    }
                }
            )
        });



        // ===============================================================
        // ===============================================================
        

        $("#details_evaluation").hide();
        
        function makeItemAppearDetails($toggle, $item) {
                $toggle.change(function () {
                    if ($toggle.is(":checked")) {
                        $item.show(500);
                        $("#explain_evaluation").hide(500);
                    } else {
                        $item.hide(500);
                        $("#explain_evaluation").show(500);
                    }
                });
            }

        makeItemAppearDetails($("#id_is_evaluation"), $("#details_evaluation"));
 

        $(".overlay").hide();
        $(".overlay_show").click(function(){ 
            value =  $(this).attr("data-parcours_id"); 
            $('.overlay_show'+value).toggle(500);
        });



        $(".group_show").hide();
        $(".group_shower").click(function(){
            value =  $(this).attr("data-parcours_id"); 
            $('.group_show'+value).toggle(500);
        });

        $(".export_shower").click(function(){
            value =  $(this).attr("data-parcours_id"); 
            $('.overlay_export'+value).toggle(500);
        });

        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.exportation_de_note').on('click' ,function () {

            let parcours_id = $(this).attr("data-parcours_id"); 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let value = $("#on_mark"+parcours_id).val(); 

            if (value=="") { alert("Vous devez renseigner cette valeur"); 
                            $("#on_mark"+parcours_id).focus();
                            return false;}

            $("#loading_export"+parcours_id).html("<i class='fa fa-spinner fa-pulse fa-fw'></i>");  
                                            
            $.ajax(
                {
                    success: function (data) {

                        $("#loading_export"+parcours_id).html("").hide(); 
                    }
                }
            )
        });




        // Pour un élève... Depuis son parcours
        $('.read_my_production').on('click', function (event) {

            let custom = $(this).attr("data-custom");
            let exercise_id = $(this).attr("data-exercise_id");
            let student_id = $(this).attr("data-student_id");

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'exercise_id': exercise_id,
                        csrfmiddlewaretoken: csrf_token,
                        'custom': custom,
                        'student_id': student_id,
                    },
                    url: "../ajax_read_my_production",
                    success: function (data) {
                        $('#my_production_paper').html(data.html);
                    }
                }
            )
        });



        // Affiche connaissant l'exercice  et le cours
        $('.header_shower').on('click', function (event) {
            let relation_id = $(this).attr("data-relation_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let parcours_id = $(this).attr("data-parcours_id");
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'relation_id': relation_id,
                        csrfmiddlewaretoken: csrf_token,
                        'parcours_id': parcours_id,
                    },
                    url: "../../ajax/course_viewer",
                    success: function (data) {
                        $('#courses_from_section').html(data.html);
                    }
                }
            )
        });



        // Affiche  un cours connaissant le parcours et le cours
        $('.course_viewer').on('click', function (event) {
            let course_id = $(this).attr("data-course_id");
            let parcours_id = $(this).attr("data-parcours_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'course_id': course_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../ajax_this_course_viewer",
                    success: function (data) {

                        $('#body_course').html(data.html);
                        if( $('#this_course_viewer') ) { $('#this_course_viewer').html(data.html);}
                        if( $('#this_course_title') ) {$('#this_course_title').html(data.title);}
                    }
                }
            )
        });


        $('body').on('click', '.projection', function () {

            var content = $(this).html();
            var screen_size = $(window).width()  ;
            var label = '<label for="customRange3" class="form-label">Taille de police</label><input type="range" value="3" class="form-range" min="3" max="5.5" step="0.5" id="customRange" style="width:200px">' ; 
     
                if (!$('#projection_div') ) {
                        $("body").append('<div class="projection_div"  id="projection_div" style="font-size:3rem"><span class="pull-right closer_projection_div" style="font-size:20px" ><i class="fa fa-times fa-2x"></i></span>'+content+'</div>');                
                    }                  
         

                if($('#projection_div img').length){ 
                                    $('.projection_div').find("img").removeAttr("style");             
                                    $('.projection_div').find("img").addClass("projection_img_live");
                                    }


                $('body').on('change', "#customRange", function (e) {
                    size  = $("#customRange").val() ; 
                    $("#projection_div").attr("style","font-size:"+size+"rem");
                });



                if($('#projection_div iframe').length) { 

                                    width = 2*parseInt($('#projection_div').find("iframe").attr("width"));
                                    height = 2*parseInt($('#projection_div').find("iframe").attr("height")); 
                                    coeff = width/height   ;                                 

                                    // if (width < screen_size){
                                    //     $('#projection_div').find("iframe").attr("width", width); 
                                    //     $('#projection_div').find("iframe").attr("height", height);
                                    // }
                                    // else{
                                        new_size = 0.9*screen_size ; 
                                        $('#projection_div').find("iframe").attr("width", new_size ); 
                                        $('#projection_div').find("iframe").attr("height", new_size / coeff );
                                    //}
                    }
        });
 

 
        $('body').on('click', ".closer_projection_div", function () {
             $("#projection_div").remove();
        });




        function display_custom_exercise_modal($actionner,$target){
              
            $actionner.on('click', function (event) {
                let customexerciseship_id = $(this).attr("data-customexercise_id");
                $($target+customexerciseship_id).toggle();
                $($target+customexerciseship_id).focus();                  
            });

        } ;

        display_custom_exercise_modal($('.custom_action_task'),"#custom_task_detail");

        display_custom_exercise_modal($('.custom_select_publish'),"#custom_detail_pub");
        display_custom_exercise_modal($('.custom_select_details'),"#custom_details");
        display_custom_exercise_modal($('.custom_sharer'),"#custom_share");

        display_custom_exercise_modal($('.custom_select_task_close'),"#custom_detail_dateur");
        display_custom_exercise_modal($('.custom_select_publish_close'),"#custom_detail_pub");
        display_custom_exercise_modal($('.custom_select_details_close'),"#custom_details");
        display_custom_exercise_modal($('.custom_select_share_close'),"#custom_share");

           
        $('.custom_select_task').on('click', function (event) {
            let relationship_id = $(this).attr("data-relationship_id");
            $("#custom_detail_dateur"+relationship_id).toggle();
            $("#custom_detail_dateur"+relationship_id).focus();
        });


        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.attribute_to_parcours').on('click', function (event) {

            let parcours_id = $(this).attr("data-parcours_id");
            let exercise_id = $(this).attr("data-exercise_id");            
            let custom = $(this).attr("data-custom");

            $("#change_parcours_exercise_id").val(exercise_id);
            $("#change_parcours_parcours_id").val(parcours_id);
            $("#change_parcours_custom").val(custom);
        });


 


        $(".click_parcours_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#folder"+parcours_id).toggle(500);
            if( $(this).find("i").hasClass("fa-folder") ) 

                { $(this).find("i").removeClass("fa-folder").addClass("fa-folder-open");}
            else 
                { $(this).find("i").removeClass("fa-folder-open").addClass("fa-folder");}

        });

        $(".click_evaluations_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#evaluations_in"+parcours_id).toggle(500);
        });


        $(".click_quizz_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#quizz_in"+parcours_id).toggle(500);
        });


        $(".click_bibliotex_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#bibliotex_in"+parcours_id).toggle(500);
        }); 
        
        $(".click_course_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#course_in"+parcours_id).toggle(500);
        });


        $(".click_flashpack_show").on('click', function (event) {
            let parcours_id = $(this).attr("data-parcours_id");
            $("#flashpacks_in"+parcours_id).toggle(500);
        }); 
        // ====================================================================================================================
        // ====================================================================================================================
        // ========================================   Reproposer une évaluation       =========================================
        // ====================================================================================================================
        // ====================================================================================================================

 
        $('.redo_eval').on('click', function (event) {

            let student_id  = $(this).data("student_id");
            let parcours_id = $(this).data("parcours_id");
            let student     = $(this).data("student_name");
            let parcours    = $(this).data("parcours_title");

            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            if (!confirm("Vous souhaitez effacer les résultats de l'élève "+student+" lors de l'évaluation "+parcours+" ? Attention cette action est irréversible. Confirmer. ")) return false;

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'student_id': student_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../redo_evaluation",
                    success: function (data) {

                        $('#redoNbr'+student_id).html("0");
                        $('#redoKnowledge'+student_id).html(data.knowledges);
                        $('#redoSkill'+student_id).html(data.skills);
                        $('#redoDuration'+student_id).html("");
                        $('#redoScore'+student_id).html("");  
                        $('.stat_mark_round'+student_id).remove();                                   
 
                    }
                }
            )
        });



        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================       Mes accordions       ============================================ 
        // ====================================================================================================================
        // ====================================================================================================================
            $('.collapsed').hide() ;
            collapser = 0 ;
            $('.accordion').on('click', function (event) {

                let target = $(this).attr("data-target");

                $(".subparcours"+target).toggle(500);

                if (collapser %2 == 0) 
                    { 
                        $("#pop"+target).removeClass('fa-chevron-down').addClass('fa-chevron-up');

                        $(".selected_tr").addClass('no_visu_on_load');
                        $("#tr"+target).removeClass('no_visu_on_load').addClass('bg_violet');
                    } 
                else 
                    {
                        $("#pop"+target).removeClass('fa-chevron-up').addClass('fa-chevron-down');

                        $(".selected_tr").removeClass('no_visu_on_load');
                        $("#tr"+target).removeClass('bg_violet');

                    }
                collapser++;                     
             }) ;
 


        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================      DIAPORAMA DE COURS       ========================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('.reset_slider').on('click', function (event) {

            slides = $('#ul_slider').children(":gt(0)") ;

           $.each( slides , function( i, val ) { 
                 val.remove() ;
                }) ;

        })


        // Affiche  un cours connaissant le parcours et le cours
        $('.built_diaporama').on('click', function (event) {
     

                var slideBox = $('#ul_slider'),
                    slideWidth = 1200 ,
                    slideQuantity = slideBox.children('li').length,
                    currentSlide = 1 ,
                    currentQuestion = 1 ;

                slideBox.css('width', slideWidth*slideQuantity);

             
                function transition(currentSlideInput, slideWidthInput){

                    var pxValue = -(currentSlideInput -1) * slideWidthInput ; 
                    slideBox.animate({
                        'left' : pxValue
                    }) ;
 

                }
 

               $('.nav button').on('click', function(){ 

         
                       var whichButton = $(this).data('nav'); 
                       console.log(whichButton);

                           if (whichButton === 'next') {

                                if (currentSlide === slideQuantity)
                                    { 
                                        currentSlide = 1 ; 
                                    }
                                else 
                                    { 
                                        currentSlide++ ; 
                                    }
                                transition(currentSlide, slideWidth )  ;

                           } else if (whichButton === 'prev') {

                                if (currentSlide === 1)
                                    { 
                                        currentSlide = slideQuantity ; 
                                    }
                                else 
                                    { 
                                        currentSlide-- ; 
                                    }
                                transition(currentSlide, slideWidth ) ;
                           }

                    });


                var screen_size = 1200  ;

                if($('#ul_slider iframe').length) { 

                        width = 2*parseInt($('#ul_slider').find("iframe").attr("width"));
                        height = 2*parseInt($('#ul_slider').find("iframe").attr("height")); 
                        coeff = width/height   ;                                 


                        new_size = screen_size ; 
                        $('#ul_slider').find("iframe").attr("width", new_size ); 
                        $('#ul_slider').find("iframe").attr("height", new_size / coeff );
                              
                    }
        });



        // Individualiser les exercices un par un
        $('.reset').on('click', function (event) {
            let nb = $(this).data("nb"); 
            let custom = $(this).data("custom");
            let group_id = $(this).data("group_id"); console.log(group_id) ; 
            let relationship_id = $(this).data("relationship_id");            
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'custom': custom,
                        'relationship_id' : relationship_id ,
                        'group_id' : group_id ,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../ajax_reset_this_exercise",
                    success: function (data) {
                        $('#reset_this_exercise_nb').html(nb);
                        $('#reset_this_exercise').html(data.html);

                    } 
                }
            )
        });



        // Individualiser les exercices un par un
        $('.individualiser').on('click', function (event) {
            let nb = $(this).data("nb"); 
            let custom = $(this).data("custom");
            let group_id = $(this).data("group_id"); 
            let relationship_id = $(this).data("relationship_id");            
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'custom': custom,
                        'relationship_id' : relationship_id ,
                        'group_id' : group_id ,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../ajax_individualise_this_exercise",
                    success: function (data) {
                        $('#indiv_this_exercise_nb').html(nb);
                        $('#indiv_this_exercise').html(data.html);

                    }
                }
            )
        });






        // Individualiser les exercices un par un
        $('.individualiser_document').on('click', function (event) {
            let nb = $(this).data("nb"); 
            let group_id = $(this).data("group_id"); 
            let relationship_id = $(this).data("relationship_id");            
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            console.log(group_id , relationship_id) ; 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'relationship_id' : relationship_id ,
                        'group_id' : group_id ,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../ajax_individualise_this_document",
                    success: function (data) {
                        $('#indiv_this_exercise_nb').html(nb);
                        $('#indiv_this_exercise').html(data.html);

                    }
                }
            )
        });














        // Individualiser les exercices un par un
        $('.delete_from_folder').on('click', function (event) {

            let parcours_id = $(this).data("parcours_id"); 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
 
                        'parcours_id' : parcours_id ,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../../parcours_delete_from_folder",
                    success: function (data) {
                        
                        $('#delete_from_folder'+parcours_id).remove();

                    }
                }
            )
        });





        // Individualiser les exercices un par un
        $('.show_hide').on('click', function (event) {

            let course_id = $(this).data("course_id"); 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'course_id' : course_id ,
                        csrfmiddlewaretoken: csrf_token,
                    },
                    url: "../../ajax_show_hide_course",
                    success: function (data) {

                        if (data.html) 
                            { $('#show_hide'+course_id).removeClass('fa-eye-slash'); $('#show_hide'+course_id).addClass('fa-eye'); } 
                        else                       
                            { $('#show_hide'+course_id).removeClass('fa-eye'); $('#show_hide'+course_id).addClass('fa-eye-slash'); }


                    }
                }
            )
        });



        // Affiche connaissant l'exercice  et le cours
        $('.subparcours_selector').on('change', function (event) {
            let parcours_id = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        csrfmiddlewaretoken: csrf_token,
                        'parcours_id': parcours_id,
                    },
                    url: "../../../ajax_subparcours_check",
 
                }
            )
        });



 
        // Permet d'avoir les vignettes de cours plus jolies
        $(".display_annoncement_for_courses").find("*").css("font-size","12px");
        $('.display_annoncement_for_courses').find("table").css("width","0px");

    });
});