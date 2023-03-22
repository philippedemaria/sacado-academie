$(document).ready(function () {
 
 
        console.log("---- NEW test accueil_accueil.js ---") ;  


        if ( $("#id_form-0-password1").length ) {   
                $("#id_form-0-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-0-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                });
            }


        if ( $("#id_form-1-password1").length ) {   
                $("#id_form-1-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-1-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                });
            }

        if ( $("#id_form-2-password1").length ) {   
                $("#id_form-2-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-2-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                });
            }

        if ( $("#id_form-3-password1").length ) {   
                $("#id_form-3-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-3-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                    
                });
            }




        if ( $("#id_form-4-password1").length ) {   
                $("#id_form-4-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-4-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                });
            }

        if ( $("#id_form-5-password1").length ) {   
                $("#id_form-5-password2").on('blur', function () {
                    let f2 = $(this).val();
                    let f1 = $("#id_form-5-password1").val();
                    if (f1 != f2) {
                        alert('La confirmation du mot de passe ne correspond pas !');
                        $("#sendit").prop("disabled", true ) ;
                    }
                    else
                        { $("#sendit").prop("disabled", false ) ; }
                    
                });
            }





        setTimeout(function(){ 
           $("#container_messages").css('display', "none"); 
        }, 3000);

        //$('[data-toggle="popover"]').popover();
        //$(".select2").select2({width: '100%'});

        $('#sendit').prop('disabled', true);
 
        $("#id_form-0-username").on('change', function () {
            let username = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: '/account/ajax/userinfo/',
                data: {
                    'username': username,
                    'csrf_token' : csrf_token ,
                },
                type: "POST",
                dataType: "json",
                success: function (data) {
                    $("#ajaxresult0").html(data["html"]);

                    if(data["test"]) 
                        { $("#sendit").prop("disabled", false ) ;} 
                    else 
                        { $("#sendit").prop("disabled", true ) ;}
                }
            });
        });

        $("#id_form-0-email").on('blur', function () {
            let email = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: '/account/ajax/userinfomail/',
                data: {
                    'email': email,
                    'csrf_token' : csrf_token ,
                },
                type: "POST",
                dataType: "json",
                success: function (data) {
                    $(".ajaxresultmail").html(data["html"]);

                    if(data["test"]) { $("#sendit").prop("disabled", false ) ;} else { $("#sendit").prop("disabled", true ) ;}
                }
            });
        });



        somme = 0
        $('#teacher_form .id_first_name').on('blur', function () {

                let lastname = $("#teacher_form .id_last_name").val().toLowerCase();
                let firstname = $("#teacher_form .id_first_name").val().toLowerCase();
 
                $("#teacher_form .username").val(lastname+firstname.charAt(0)) ;
                $("#teacher_form .email").val(firstname+"."+lastname+"@") ;

                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let username = lastname +  firstname  ;
    
                $.ajax({
                    url: '../account/ajax/userinfo/',
                    data: {
                        'username': username,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $(".ajaxresult").html(data["html"]);
                        if (data["test"]) { $('#teacher_form .sendit').prop('disabled', false) } else { somme = somme + 1 }
                        if (somme > 1 ) { $('#teacher_form .sendit').prop('disabled', true); }  
                    }
                });
            });

 
        $('#student_form .sendit').prop('disabled', true);
        sommeS = 2

        $("#student_form #id_username").on('keyup', function () {
            let username = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: '/account/ajax/userinfo/',
                type: "POST",
                data: {
                    'username': username,
                    csrfmiddlewaretoken: csrf_token,    
                },
                dataType: 'json',
                success: function (data) {
                    $("#student_form .ajaxresult").html(data["html"]);
                    sommeS = sommeS - 1;
                } 
            });
        });

        $("#student_form #id_group").on('keyup', function () {
            let groupe_code = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: '/account/ajax/courseinfo/',
                type: "POST",
                data: {
                    'groupe_code': groupe_code,
                    csrfmiddlewaretoken: csrf_token,    
                },
                dataType: 'json',
                success: function (data) {
                    $("#student_form  .verif_course").html(data["htmlg"]);
                    sommeS = sommeS - 1;
                }
            });
        });

        $('#student_form .id_first_name').on('blur', function () {

                let lastname = $("#student_form .id_last_name").val().toLowerCase();
                let firstname = $("#student_form .id_first_name").val().toLowerCase();
 
                $("#student_form .username").val(lastname+firstname) ;

                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
              
                let username = lastname +  firstname  ;
    
                $.ajax({
                    url: '../account/ajax/userinfo/',
                    data: {
                        'username': username,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
 
                        $(".ajaxresult").html(data["html"]);
                        if (data["test"]) {  sommeS = sommeS - 1 }  
                        if (sommeS < 1) {$('#student_form .sendit').prop('disabled', false);   } else {$('#student_form .sendit').prop('disabled', true);   }  
                    }
                });
            });


        $('.is_child_exist').prop('disabled', true);

        sommeP = 2 ;
        $("#parent_form #id_username").on('blur', function () {
            let username = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: '/account/ajax/userinfo/',
                type: "POST",
                data: {
                    'username': username,
                    csrfmiddlewaretoken: csrf_token,    
                },
                dataType: 'json',
                success: function (data) {
                    $("#parent_form .ajaxresult").html(data["html"]);
                }
            });
        });


        $('#parent_form .id_first_name').on('blur', function () {

                let lastname = $("#parent_form #id_last_name").val().toLowerCase();
                let firstname = $("#parent_form #id_first_name").val().toLowerCase();
 
                $("#parent_form #id_username").val(lastname+firstname) ;
                $("#parent_form #id_email").val(firstname+"."+lastname+"@") ;


                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
              
                let username = lastname +  firstname  ;
    
                $.ajax({
                    url: '../account/ajax/userinfo/',
                    data: {
                        'username': username,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
 
                        $("#parent_form .ajaxresult").html(data["html"]);
                        if (data["test"]) {  sommeP = sommeP - 1 }  
                        if (sommeP < 1) {$('#parent_form .is_child_exist').prop('disabled', false);   } else {$('#parent_form .is_child_exist').prop('disabled', true);   }  
                    }
                });
            });


        $('#code_student').on('keyup', function () {

                 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let code_student =  $(this).val()  ;

                $.ajax({
                    url: '../account/ajax/control_code_student/',
                    data: {
                        'code_student': code_student,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
 
                        $("#parent_form .verif_course").html(data["html"]);
                       
                        if (data["test"]  ) {  sommeP = sommeP - 1 ; }  
                        if (sommeP < 1 ) { $('#parent_form .is_child_exist').prop('disabled', false);   }  else { $('#parent_form .is_child_exist').prop('disabled', true);   }  
                    }
                });
            });


        $("#join_alone").hide();
        $("#parcours_div").hide();
        $('#level_selected').toggle(500); 


        $("#choose_alone").click(function(){

                $('#level_choose').toggle(500);
                $('#level_selected').toggle(500); 
                $('#join_alone').toggle(500);
                $('#join_group').toggle(500); 
                $('#id_group').toggle(500); 

                if ($(this).is(":checked") && (sommeS == 1)) {    
     
                $('#send_alone').prop('disabled', false);
                } 
                else{
                $('#send_alone').prop('disabled', true);
                }
            });


        $("#send_alone").click(function(){


            level_selector = $('#level_selector').val(); 
            
            if (level_selector == "") {
                alert('Vous devez sélectionner au moins un niveau');
                return false;
            }
            });


        // Gestion des formulaires de l'adhésion
        $('.family').hide() ;
        $('.one').show() ;

        calculate_rate('#zero_child', '.one',"Moi-même",0);
        calculate_rate('#one_child', '.one',"1 enfant",1);
        calculate_rate('#two_children', '.two',"2 enfants",2);
        calculate_rate('#three_children', '.three',"3 enfants",3);
        calculate_rate('#four_children', '.four',"4 enfants",4);
        calculate_rate('#more_children', '.more',"5 enfants",5) ;


        function calculate_rate($target, $number,$n,$nb){


            $($target).click(function(){

                // Afficahge des montants
                $('.family_selected').removeAttr("checked");
                $(this).children().attr("checked", "checked");
                $('.nb_child').val($nb);
                $('.child').html("").html($n); 
                $(".family_selected").addClass("btn-violet_border").removeClass("btn-violet_border_active");                
                $(this).addClass("btn-violet_border_active").removeClass("btn-violet_border");
                $('.family').hide() ;
                $($number).show() ;
            });

        }

 


        $('#add_parent').on('click', function (event) { 

            nb_parent = $('#id_form-TOTAL_FORMS').val();
 
            var object = $('#formsetZone').html(); 
            $("#pasteZone").html(object) ;
            

            $("#pasteZone input").each(function(){ 
                $(this).attr('id',$(this).attr('id').replace('__prefix__',nb_parent));
                $(this).attr('name',$(this).attr('name').replace('__prefix__',nb_parent));
            });

            $('#id_form-TOTAL_FORMS').val( parseInt(nb_parent)+1 ) ; 


            $("#add_parent").hide(500);
 
        });


        $(document).on('click', '.delete_button', function () {
            $("#pasteZone").html("") ; 
            $("#add_parent").show(500);
        });

        if ($('#id_form-0-cgu')) { $('#id_form-0-cgu').prop('checked', false); } 
        if ($('#id_cgu')) { $('#id_cgu').prop('checked', false); }


 

 
        $("#fonctions").hide();
        $('#show_fonctions').on('click', function (event) { 
              $('#fonctions').toggle(500); 
        });

        $('#close_tab').on('click', function (event) { 
              $('#fonctions').toggle(500); 
        });


        $('#close_form').on('click', function (event) { 
              $('#renew_form_school').toggle(500); 
        });

        $('#id_nbstudents').on('change', function () {
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let nbr_students = $("#id_nbstudents").val() ;
                $.ajax({
                    url: 'ajax_get_price',
                    data: {
                        'nbr_students': nbr_students,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
 
                        $("#somme").val(data["price"]);
 
                    }
                });
            });


        var len = $(".username").length - 1;

        for (i=0;i<len;i++)
        {


        }



            $(".username").on('change', function () {
                let username_id = $(this).attr("id");

                tab = username_id.split("-");
                determination( tab[1] )

            });


        function determination(i) {
                let username = $("#id_form-"+i+"-username").val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
     
                $.ajax({
                    url: '/account/ajax/userinfo/',
                    type: "POST",
                    data: {
                        'username': username,
                        csrfmiddlewaretoken: csrf_token,    
                    },
                    dataType: 'json',
                    success: function (data) {
                        $("#ajaxresult"+i).html(data["html"]);
                    } 
                });
            }




 
        $('#on_line').on('click', function (event) { 
              $('.this_card').addClass("show_div_for_payment"); 
              $('#show_on_line').removeClass("show_div_for_payment"); 
        });

 
        $('#virement_bancaire').on('click', function (event) { 
              $('.this_card').addClass("show_div_for_payment"); 
              $('#show_virement_bancaire').removeClass("show_div_for_payment"); 

        });

 
        $('#envoi_postal').on('click', function (event) { 
              $('.this_card').addClass("show_div_for_payment"); 
              $('#show_envoi_postal').removeClass("show_div_for_payment"); 
        });

        $("#id_gar").prop("checked",false);






        $('.opener_k').hide() ;
        $('.opener_e').hide() ;
 

        $('.opener').on('click' ,function () { 
            $('.opener_k').hide() ;

            if( $(this).hasClass("out") )
            {
                $(".opener ~ .opened"+this.id).show();
                $(this).removeClass("out").addClass("in");
                $(this).find('.fa').removeClass('fa-caret-right').addClass('fa-caret-down'); 
            }
            else 
            {
                $(".opener ~ .opened"+this.id).hide();  
                $(this).removeClass("in").addClass("out");
                $(this).find('.fa').removeClass('fa-caret-down').addClass('fa-caret-right');     
            }
 
        });



        $('.opener_k').on('click' ,function () { 
            $('.opener_e').hide() ;

            if( $(this).hasClass("out") )
                {
                $(".opener_k ~ .openedk"+this.id).show();
                $(this).removeClass("out").addClass("in");
                $(this).find('.fa').removeClass('fa-caret-right').addClass('fa-caret-down');
                }
            else 
            {
                $(".opener_k ~ .openedk"+this.id).hide();  
                $(this).removeClass("in").addClass("out");
                $(this).find('.fa').removeClass('fa-caret-down').addClass('fa-caret-right');            
            }
 
        });







        $(".subject_div").on('click', function () {

            let subject_id = $(this).attr("data-subject_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $(".subject_div").removeClass("active_subject_div");
            $(this).addClass("active_subject_div"); 


            $.ajax({
                
                url: '/ajax_get_subject/',
                type: "POST",
                data: {
                    'subject_id': subject_id,
                     csrfmiddlewaretoken: csrf_token,    
                },
                dataType: 'json',
                success: function (data) {
                    $("#sacado_subject").html(data["html"]);

                } 

            });
        }); 





      $(".regular").slick({
            slidesToShow: 3,
            slidesToScroll: 3,
            autoplay: false,
            autoplaySpeed: 2000,        
            dots: false,
            infinite: true,
 
      });




        $("#accept_rgpd").on('click', function () {
                let date = new Date(Date.now()+86400000*180);
                date = date.toUTCString();
                document.cookie = "cookie_rgpd_accepted=True;path=/;   expires="+date;
                console.log(document.cookie) ;
                $("#display_rgpd").remove();
            }); 


        $("#no_accept_rgpd").on('click', function () {
                let date = new Date(Date.now()+86400000*180);
                date = date.toUTCString();
                document.cookie = "cookie_rgpd_accepted=False;path=/;   expires="+date;
                $("#display_rgpd").remove();

            });
 


        


        $( "#photo_background1" ).hover(function() {
            surcouche("#photo_background_texte1") ;
        });

        $( "#photo_background2" ).hover(function() {
            surcouche("#photo_background_texte2") ;
        });

        $( "#photo_background3" ).hover(function() {
            surcouche("#photo_background_texte3") ;
        });

        $( "#photo_background4" ).hover(function() {
            surcouche("#photo_background_texte4") ;
        });

        $( "#photo_background5" ).hover(function() {
            surcouche("#photo_background_texte5") ;
        });

        $( "#photo_background6" ).hover(function() {
            surcouche("#photo_background_texte6") ;
        });


        function surcouche(over) {

              $( over ).animate({
                height: "toggle"
              }, 1000 );

            }



        $("#show_detail_display_suivi").hide();
        $("#show_detail_display_perso").hide();


        $("#detail_display_suivi").click(function(){

                $('#show_detail_display_suivi').toggle(500);
            });


        $("#detail_display_perso").click(function(){

                $('#show_detail_display_perso').toggle(500);
            });



});

 
