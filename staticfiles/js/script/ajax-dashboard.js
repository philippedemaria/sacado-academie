define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-dashboard.js OK");
 

          $(window).on('load', function () {
            if ($('#preloader').length) {
              $('#preloader').delay(100).fadeOut('slow', function () {
                $(this).remove();
              });
            }
          });


        setTimeout(function(){ 
           $(".messages").css('display', "none"); 
        }, 6000);

        //////////////////////////////////////////////////////////////////////////////////////////////////
        // ACTIONNER LA FLECHE DES ACCORDIONS
        //////////////////////////////////////////////////////////////////////////////////////////////////
        $('.actionner_accordion').on('click', function (event) {
                let loop = $(this).data("loop") ; 
                if  ($("#collapser_angle"+loop).hasClass("fa-angle-up"))
                {
                    setTimeout( change_direction('bottom',loop) , 1000 ); 
                }
                else{
                    setTimeout( change_direction('top',loop) , 1000 );
                }
            });

        function change_direction(sens,loop) {               

                if (sens == 'top')
                {
                    $("#collapser_angle"+loop).addClass("fa-angle-up") ;    
                    $("#collapser_angle"+loop).removeClass("fa-angle-down") ; 
                }
                else 
                {
                    $("#collapser_angle"+loop).removeClass("fa-angle-up") ; 
                    $("#collapser_angle"+loop).addClass("fa-angle-down") ; 
                }
            }

        function AnimateRotate($elem , angle) {
                // we use a pseudo object for the animation
                // (starts from `0` to `angle`), you can name it as you want
                $({deg: 180}).animate({deg: angle}, {
                    duration: 500,
                    step: function(now) {
                        // in the step-callback (that is fired each step of the animation),
                        // you can use the `now` paramter which contains the current
                        // animation-position (`0` up to `angle`)
                        $elem.css({
                            transform: 'rotate(' + now + 'deg)'
                        });
                    }
                });
            }
        //////////////////////////////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////////////////////////////////////

        $('.helper_div_text').on('click', function (event) {

            let condition = $(this).data("helper_text") ;

            if (condition == "flashpack") 
            {
                $("#helper_div_title").html("Les flashpack ");
                value = $("#helper_flashpack_text").html();
            }
            else if (condition == "bibliotex") 
            {
                $("#helper_div_title").html("Les biblioTex");
                value = $("#helper_bibliotex_text").html();
            }
            else if (condition == "quizz") 
            {
                $("#helper_div_title").html("Les quizz "); 
                value = $("#helper_quizz_text").html();
            }

            $("#helper_div_in").html(value) ;
        });

        //////////////////////////////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////////////////////////////////////
        //////////////////////////////////////////////////////////////////////////////////////////////////

        $('#show_help_from_tdb').on('click', function (event) {
            $("#help_from_tdb").toggle(300) ;
        });

        // $('.collapse').not(':first').collapse();Collapse all but the first row on the page.
        // This section makes the search work.
        
          var searchTerm, panelContainerId;
          $('#accordion_search_bar').on('change keyup', function() {
            searchTerm = $(this).val();
            $('#accordion > .panel').each(function() {
              panelContainerId = '#' + $(this).attr('id');

              // Makes search to be case insensitive 
              $.extend($.expr[':'], {
                'contains': function(elem, i, match, array) {
                  return (elem.textContent || elem.innerText || '').toLowerCase()
                    .indexOf((match[3] || "").toLowerCase()) >= 0;
                }
              });

              // END Makes search to be case insesitive

              // Show and Hide Triggers
              $(panelContainerId + ':not(:contains(' + searchTerm + '))').hide(); //Hide the rows that done contain the search query.
              $(panelContainerId + ':contains(' + searchTerm + ')').show(); //Show the rows that do!

            });
          });
  
        // End Show and Hide Triggers

        // END This section makes the search work.



        $('#id_child').on('keyup', function () {

                 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let code_student =  $(this).val()  ;

                $.ajax({
                    url: 'account/ajax/control_code_student/',
                    data: {
                        'code_student': code_student,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
 
                        $("#verif_child").html(data["html"]);
  
                    }
                });
            });
        // ====================================================================================================================
        // ====================================================================================================================
        // =========================================   check username exist  ================================================== 
        // ====================================================================================================================
        // ====================================================================================================================


        $("#id_username").on('blur', function () {
            let username = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            console.log(username);
            $.ajax({
                url: '/account/ajax/userinfo/',

                data: {
                    'username': username,
                    'csrf_token' : csrf_token ,
                },
                type: "POST",
                dataType: "json",
                success: function (data) {
                    $("#ajaxresult").html(data["html"]);

                    if(data["test"]) { $("#submitter").attr("disabled", false ) ;} else { $("#submitter").attr("disabled", true ) ;}
                } 
            });
        });



        $("#id_email").on('blur', function () {
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

                    if(data["test"]) { $("#submitter").prop("disabled", false ) ;} else { $("#submitter").prop("disabled", true ) ;}
                }
            });
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // ===============================================   Les outils péda ================================================== 
        // ====================================================================================================================
        // ====================================================================================================================
        // Affiche dans la modal le modèle pour récupérer un exercice custom
        $('body').on('click', '.delete_my_tool' , function (event) {  

            let tool_id = $(this).attr("data-tool_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'tool_id': tool_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../tool/delete_my_tool",
                    success: function (data) {

                        $('#delete_my_tool'+tool_id).remove();
 
                    }
                }
            )
         });
        // ====================================================================================================================
        // ====================================================================================================================
        // ===============================================   Version mobile  ================================================== 
        // ====================================================================================================================
        // ====================================================================================================================


        $('#mobile_version_button').click(function(event) {
          if ($('.navbarLeft').hasClass('navbarLeft_none')) {
            $('.navbarLeft').removeClass('navbarLeft_none').addClass('navbarLeft_show');

            content = $(".navbar-right").html() ;

            $(".navbarRight-nav").append("<hr/>") ;
            $(".navbarRight-nav").append(content) ;
            $(".navbarRight-nav").find(".caret").addClass("fa fa-caret-up").removeClass("caret") ;
          }
          event.preventDefault();
        });

        $('#mobile_version_button_closer').click(function(event) {
          if ($('.navbarLeft').hasClass('navbarLeft_show')) {
            $('.navbarLeft').removeClass('navbarLeft_show').addClass('navbarLeft_none');
            $(".navbarRight-nav").html("") ;
          }
          event.preventDefault();
        });

 
        // ====================================================================================================================
        // ====================================================================================================================
        // =================================   Toggle sur la div des élèves d'un groupe ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('#teacher_to_student_div').hide() ;
        $('#teacher_to_student_view').on('click', function (event) {
            $('#teacher_to_student_div').toggle() ;
        });
        // ====================================================================================================================
        // ====================================================================================================================
        // =================================   Toggle sur la div des élèves d'un groupe ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================

 

        $('#preloader_groups').hide() ;
        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('#televerser_groups').on('click', function (event) {
            $('#preloader_groups').show() ;
        });



        $(".accordion_click").click(function(event) { 

            if ($(this).hasClass('fa-angle-down')) {
                $(this).removeClass('fa-angle-down').addClass('fa-angle-up');
              }
            else
            {
                $(this).removeClass('fa-angle-up').addClass('fa-angle-down');
            }
            event.preventDefault();        
        }); 



        $(".hide_school").hide() ;
        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.show_school_click').on('click', function (event) { 
  
                let school_id = $(this).attr("data-school_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'school_id': school_id ,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "school/ajax_get_this_school_in_session" ,
                        success: function (data) {

                            if (!$(".selector_school").children().hasClass('hide_school')) { $(".selector_school").addClass('hide_school'); }

                            if ($(this).children().hasClass('fa-angle-right')) {
                                $(this).children().removeClass('fa-angle-right').addClass('fa-angle-up');

                              }
                            else
                            {
                                $(this).children().removeClass('fa-angle-up').addClass('fa-angle-right');
                            }

                            $(".hide_school").hide(500) ;
                            $("#show_school"+school_id).show(500) ;
                            event.preventDefault();                            
                        }
                    }
                )
        });


  
        $(".overlay").hide();
        $(".overdiv_show").click(function(){
            value =  $(this).attr("data-student_id"); 
            $('.overdiv_show'+value).toggle(500);
        });


        $('.content-wrapper').removeAttr("style");




        $('.closer_notification').click(function(event) {
            $('.dropdown').removeClass('active');
            $('.dropdown').parent().addClass('active');
            $('.notification-container').removeClass('selected').addClass('dismiss');
            $('#documents').find('.bi').removeClass("bi-folder2-open").addClass("bi-folder");
            $('#account').find('.bi').removeClass("bi-person-square").addClass("bi-person-circle");

        });


        $('#documents').click(function(event) {
                appear_panel('documents');
        });


        $('#tools').click(function(event) {
                appear_panel('tools')
        });

        $('#admin').click(function(event) {
                appear_panel('admin')
        });

        $('#account').click(function(event) {
                appear_panel('account');
        });


        function appear_panel(target) {
          if ($('#notification-'+target).hasClass('dismiss')) {
            $('.dropdown').removeClass('active');
            $('.main').removeClass('active');
            $('#'+target).parent().addClass('active');
            $('.notification-container').removeClass('selected').addClass('dismiss');
            $('#notification-'+target).removeClass('dismiss').addClass('selected').show();

            if (target == 'documents'){ 
                $('#'+target).find('.bi').addClass("bi-folder2-open").removeClass("bi-folder");                
            }
            else if(target == 'account'){
                $('#'+target).find('.bi').addClass("bi-person-square").removeClass("bi-person-circle");
            }
            else if(target == 'tools'){
                $('#'+target).find('.bi').addClass("bi-webcam-fill").removeClass("bi-webcam");
            }
            else if(target == 'admin'){
                $('#'+target).find('.bi').addClass("bi-cloud-fog2").removeClass("bi-cloud");
            }

          }
          else{
            $('#notification-'+target).removeClass('selected').addClass('dismiss');
            $('#documents').find('.bi').removeClass("bi-folder2-open").addClass("bi-folder");
            $('#account').find('.bi').removeClass("bi-person-square").addClass("bi-person-circle");
            $('#tools').find('.bi').removeClass("bi-webcam-fill").addClass("bi-webcam");
            $('#admin').find('.bi').removeClass("bi-cloud-fog2").addClass("bi-cloud");
          }
          event.preventDefault();
        } 


 


        $('#closeAccount').click(function(event) {
          if ($('#notification-account').hasClass('selected')) {
            $('#notification-account').removeClass('selected').addClass('dismiss');
            $('#notification-tools').removeClass('selected').addClass('dismiss');
            $('#documents').find('.bi').removeClass("bi-folder2-open").addClass("bi-folder");
            $('#account').find('.bi').removeClass("bi-person-square").addClass("bi-person-circle");
            $('#tools').find('.bi').removeClass("bi-webcam-fill").addClass("bi-webcam");
            $('#admin').find('.bi').removeClass("bi-cloud-fog2").addClass("bi-cloud");
          }
          event.preventDefault();
        });

        $('#closeDocuments').click(function(event) {
          if ($('#notification-documents').hasClass('selected')) {
            $('#notification-documents').removeClass('selected').addClass('dismiss');
            $('#notification-tools').removeClass('selected').addClass('dismiss');
            $('#documents').find('.bi').removeClass("bi-folder2-open").addClass("bi-folder");
            $('#account').find('.bi').removeClass("bi-person-square").addClass("bi-person-circle");
            $('#tools').find('.bi').removeClass("bi-webcam-fill").addClass("bi-webcam");
            $('#admin').find('.bi').removeClass("bi-cloud-fog2").addClass("bi-cloud");
          }
          event.preventDefault();
        });


 
 
        $('#closeTools').click(function(event) {
          if ($('#notification-tools').hasClass('selected')) {
            $('#notification-tools').removeClass('selected').addClass('dismiss');
            $('#notification-admin').removeClass('selected').addClass('dismiss');
            $('#documents').find('.bi').removeClass("bi-folder2-open").addClass("bi-folder");
            $('#account').find('.bi').removeClass("bi-person-square").addClass("bi-person-circle");
            $('#tools').find('.bi').removeClass("bi-webcam-fill").addClass("bi-webcam");
            $('#admin').find('.bi').removeClass("bi-cloud-fog2").addClass("bi-cloud");
          }
          event.preventDefault();
        });



 

 


        $('#right_menu_open').mouseover(function(event) {    
            $('#right_menu').show();
          event.preventDefault();
        });


        $('#right_menu_Close').click(function(event) {
            $('#right_menu').hide();
          event.preventDefault();
        });

         $('.menu_right_div').mouseover(function(event) {
            $('#right_menu').show();
        });

         $('.menu_right_div').mouseout(function(event) {
            $('#right_menu').hide();
        });


 

        var show = 0 ;

        $('.detail_student').click(function(event) { 
          if ( show%2 == 0 ) 
            {
                $('#notification-perso').removeClass('dismissR').addClass('selectedR').show();

                let student_id =  $(this).attr("data-student_id");  
                let theme_id =  $(this).attr("data-theme_id"); 
                let group_id =  $(this).attr("data-group_id"); 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax({
                    url: '../../../../account/ajax_detail_student/'  ,
                    data: {
                        'student_id': student_id,
                        'theme_id': theme_id,
                        'group_id': group_id,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $("#detail_of_student").html("").html(data["html"]);
     
                        $('#closeStudent').click(function(event) {
                            show--;
                            if ($('#notification-perso').hasClass('selectedR')) 
                            {
                            $('#notification-perso').removeClass('selectedR').addClass('dismissR');
                            }
                            event.preventDefault();
                        });


                    }
                });
 

            }
            else
            {
                $('#notification-perso').removeClass('selectedR').addClass('dismissR');
            }
            event.preventDefault();        
            show ++ ;
        });


        var view = 0 ;
        $('.detail_student_exercise').click(function(event) {  
          if ( view%2 == 0 ) 
            {
                $('#notification-perso').removeClass('dismissR').addClass('selectedR').show();

                let student_id =  $(this).attr("data-student_id");  
                let parcours_id =  $(this).attr("data-parcours_id"); 
 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                $.ajax({
                    url: '../../../../account/ajax_detail_student_exercise/'  ,
                    data: {
                        'student_id': student_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $("#detail_of_student").html("").html(data["html"]);
     
                        $('#closeStudent').click(function(event) {
                            view--;
                            if ($('#notification-perso').hasClass('selectedR')) 
                            {
                            $('#notification-perso').removeClass('selectedR').addClass('dismissR');
                            }
                            event.preventDefault();
                        });
                    }
                });
            }
            else
            {
                $('#notification-perso').removeClass('selectedR').addClass('dismissR');
            }
            event.preventDefault();        
            view ++ ;
        });



        $('.detail_parcours').click(function(event) { 
          if ( show%2 == 0 ) 
            {
                $('#notification-perso').removeClass('dismissR').addClass('selectedR').show();

                let exercise_id =  $(this).attr("data-exercise_id");  
                let parcours_id =  $(this).attr("data-parcours_id");  
                let num_exo =  $(this).attr("data-num_exo");  
                let custom =  $(this).attr("data-custom"); 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax({
                    url: '../../../../qcm/ajax_detail_parcours/'  ,
                    data: {
                        'exercise_id': exercise_id,
                        'parcours_id': parcours_id,
                        'num_exo': num_exo,
                        'custom': custom,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $("#detail_of_student").html("").html(data["html"]);
     
                        $('#closeStudent').click(function(event) {
                            show--;
                            if ($('#notification-perso').hasClass('selectedR')) 
                            {
                            $('#notification-perso').removeClass('selectedR').addClass('dismissR');
                            }
                            event.preventDefault();
                        });


                    }
                });
 

            }
            else
            {
                $('#notification-perso').removeClass('selectedR').addClass('dismissR');
            }
            event.preventDefault();        
            show ++ ;
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // =================================   Toggle sur la div des élèves d'un groupe ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('#handler_order_exercises').click(function(event) { 
          if ( show%2 == 0 ) 
            {
                $('#order_exercises').removeClass('dismissR').addClass('selectedR').show();
            }
            else
            {
                $('#order_exercises').removeClass('selectedR').addClass('dismissR');
            }
            event.preventDefault();        
            show ++ ;
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // =================================   Toggle sur la div des élèves d'un groupe ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('.detail_student_parcours').click(function(event) { 
          if ( show%2 == 0 ) 
            {
                $('#notification-perso').removeClass('dismissR').addClass('selectedR').show();

                let student_id =  $(this).attr("data-student_id");  
                let parcours_id =  $(this).attr("data-parcours_id"); 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax({
                    url: '../../../../account/ajax_detail_student_parcours/'  ,
                    data: {
                        'student_id': student_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $("#detail_of_student").html("").html(data["html"]);
     
                        $('#closeStudent').click(function(event) {
                            show--;
                            if ($('#notification-perso').hasClass('selectedR')) 
                            {
                            $('#notification-perso').removeClass('selectedR').addClass('dismissR');
                            }
                            event.preventDefault();
                        });


                    }
                });
 

            }
            else
            {
                $('#notification-perso').removeClass('selectedR').addClass('dismissR');
            }
            event.preventDefault();        
            show ++ ;
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // ===============================   Toggle sur la div des élèves d'un parcours ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================
        $("#parcours_div").hide();
        $("#select_parcours_div").click(function(){
            $('#parcours_div').toggle(500);
        });



        // ====================================================================================================================
        // ====================================================================================================================
        // ===============================   Toggle sur la div des élèves d'un parcours ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================
        $("#collapser").hide();
        $("#show_collapser").click(function(){
            $('#collapser').toggle(500);
        });






        // ====================================================================================================================
        // ====================================================================================================================
        // ==================================================   uncollapsed    ================================================ 
        // ====================================================================================================================
        // ====================================================================================================================
        // $('.listing_div').hide();
        $(".un_collapsed").click(function(){

            let my_div = $(this).parent().parent().parent();
            if ($(this).find('i').hasClass("fa-angle-down"))

            {

            my_div.removeClass('documents_div');
            $('.documents_div').animate({height: "0%", }, 750 ) ;
            my_div.animate({height: "100%", }, 750, function() {
                                                                my_div.removeClass('documents_div_shadow');
                                                                
                                                                })  ;

            $(this).find('i').addClass('fa-angle-up').removeClass('fa-angle-down' );  
            $('.shadow_bottom').hide();
            //$('.listing_div').show();

            }
            else
            {


            my_div.addClass('documents_div');
            $('.documents_div').animate({height: "255px", }, 750, function() {
                                                                                my_div.addClass('documents_div_shadow');
                                                                                            $('.shadow_bottom').show(); 
                                                                                 
                                                                          })  ; 
            
            $(this).find('i').removeClass('fa-angle-up').addClass('fa-angle-down'); 

            //$('.listing_div').hide();          
            }


        });



        // ====================================================================================================================
        // ====================================================================================================================
        // =================================   Toggle sur la div des élèves d'un groupe ======================================= 
        // ====================================================================================================================
        // ====================================================================================================================
        $(".group_show").hide();
        $(".group_shower").click(function(){
            value =  $(this).attr("data-group_id"); 
            $('#group_show'+value).toggle(500);
        });


        $('body').on('click', '.bibliotex_shower' , function (event) {
                let bibliotex_id = $(this).data("bibliotex_id");
                $("#bibliotex_show"+bibliotex_id).toggle(500);

            });



        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.menuaction').on('click', function (event) {
            let group_id = $(this).attr("data-group_id");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'group_id': group_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "group/ajax/chargelisting",
                    success: function (data) {
                        $('#modal_group_name').html(data.html_modal_group_name);
                        $('#list_students').html(data.html_list_students);
                    }
                }
            )
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================       parcours par défaut     ========================================= 
        // ====================================================================================================================
        // ====================================================================================================================
        $("#level_selected_id").on('change', function () { 
            let level_selected_id = $(this).val();
            if (level_selected_id == " ") { alert("Sélectionner un niveau") ; return false ;}
            let data_url = $(this).attr("data-url"); 
            if (data_url == "yes") { url =  'qcm/ajax/parcours_default' ; } else { url =  'ajax/parcours_default' ; } 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax({
                url: url ,
                type: "POST",
                data: {
                    'level_selected_id': level_selected_id,
                    csrfmiddlewaretoken: csrf_token,    
                },
                dataType: 'json',
                success: function (data) {
                    $("#parcours_shower").html(data.html);

 
                }
            });
  
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================    Fermeture du volet admin    ========================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('#closeAdmin').click(function(event) {
          if ($('#notification-admin').hasClass('selected')) {
            $('#notification-admin').removeClass('selected').addClass('dismiss');
          }
          event.preventDefault();
        });

        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================    Recherhe d'un exercice     ========================================= 
        // ====================================================================================================================
        // ====================================================================================================================

        $('#search').on('keyup', function () {


            let search =  $(this).val()  ;   
            let from =  $("#from").val()  ;             
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            if (from) { urlform = '../../qcm/ajax_search_exercise' ;}   else { urlform = 'qcm/ajax_search_exercise' ;} 
          
            if (search.length > 5)

            { 
                $.ajax({
                    url: urlform ,
                    data: {
                        'search': search,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                        $("#search_result").html("").html(data["html"]);
                    }
                });
            }

        });


        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================    Lire les nouveauté      ============================================ 
        // ====================================================================================================================
        // ====================================================================================================================
        $('#reader_new').on('click', function (event) {
 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        csrfmiddlewaretoken: csrf_token,   
                    },
                    url: "sendmail/ajax/reader_communication/",
                    success: function (data) {
                        $('#reader_new').removeClass('btn-danger').addClass('btn-default');
                        $('#advises').hide(500);
                    }
                }
            )
        });
        // ====================================================================================================================
        // ====================================================================================================================
        // ============================================    Rejoindre un  cours     ============================================ 
        // ====================================================================================================================
        // ====================================================================================================================


        $('#aggregate_form').hide();  
        $('#aggregate_groupe').click(function(event) {
                 $('#aggregate_form').toggle(500);  
            });


        $('#id_groupe').on('keyup', function () {
             
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();        
            let groupe_code =  $(this).val()  ;

            $.ajax({
                type: "POST",
                dataType: "json",
                url: '../account/ajax/courseinfo/',
                data: {
                    'groupe_code': groupe_code,
                    csrfmiddlewaretoken: csrf_token,                        
                },
                success: function (data) {

                    $(".verif_course").html(data["htmlg"]); 
                     $('#registerstudent').prop("disabled", false);
                }
            });
        });


        $('#aggregate_parcours_form').hide();  
        $('#aggregate_parcours').click(function(event) {
                 $('#aggregate_parcours_form').toggle(500);  
            });


        $('#id_parcours').on('keyup', function () {
             
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
          

            let code =  $(this).val()  ;

            $.ajax({
                url: '../qcm/ajax_parcoursinfo/',
                data: {
                    'code': code,
                    csrfmiddlewaretoken: csrf_token,                        
                },
                type: "POST",
                dataType: "json",
                success: function (data) {

                    $(".verif_parcours").html(data["htmlg"]);
 
                }
            });
        }); 

        // ====================================================================================================================
        // ====================================================================================================================
        // ===================================== Organisation du parcours et tri   ============================================ 
        // ====================================================================================================================
        // ====================================================================================================================
        $('#closeOrganiser').click(function(event) {
          if ($('#order_exercises').hasClass('selectedR')) {
            $('#order_exercises').removeClass('selectedR').addClass('dismissR');
          }
          event.preventDefault();
        });
 

        function sorter_exercises($div_class , $exercise_class ) { 

                $($div_class).sortable({
                    cursor: "move",
                    swap: true,    
                    animation: 150,
                    distance: 10,
                    revert: true,
                    tolerance: "pointer" , 
                    start: function( event, ui ) { 
                           $(ui.item).css("box-shadow", "10px 5px 10px gray"); 
                       },
                    stop: function (event, ui) {

                        let parcours = $("#parcours").val();
                        var valeurs = "";
                        var customizes = "";

                        $($exercise_class).each(function() {
                            cstm = parseInt($(this).attr("data-custom"));
                            let div_exercise_id = $(this).val();
                            valeurs = valeurs + div_exercise_id +"-";
                            customizes = customizes + cstm +"-";
                        });


                        $(ui.item).css("box-shadow", "0px 0px 0px transparent");  

                        $.ajax({
                                data:   { 'valeurs': valeurs ,  'parcours' : parcours,'customizes' : customizes } ,    
                                type: "POST",
                                dataType: "json",
                                url: "../../ajax/sort_exercise" 
                            }); 
                        }
                    });
                }

 


        function sorter_sequence($div_class , $exercise_class ) {

                $($div_class).sortable({
                    cursor: "move",
                    swap: true,    
                    animation: 150,
                    distance: 10,
                    revert: true,
                    tolerance: "pointer" , 
                    start: function( event, ui ) { 
                           $(ui.item).css("box-shadow", "10px 5px 10px gray"); 
                       },
                    stop: function (event, ui) {

                        var valeurs = "";

                        $($exercise_class).each(function() {
                            let div_exercise_id = $(this).val();
                            valeurs = valeurs + div_exercise_id +"-";
                        });

                        console.log(valeurs) ;

                        $(ui.item).css("box-shadow", "0px 0px 0px transparent");  

                        $.ajax({
                                data:   { 'valeurs': valeurs ,} ,    
                                type: "POST",
                                dataType: "json",
                                url: "../../ajax/sort_sequence" 
                            }); 
                        }
                    });
                }    

        sorter_sequence('#sequence_sorter' , ".relationship_id_sequence");
        sorter_sequence('#exercise_sortable' , ".div_relationship_id");


        sorter_exercises('#exercise_sorter' , ".div_exercise_id");
        sorter_exercises('#exercise_sortable_list' , ".sorted_exercise_id");

        function sorter_parcours($div_class , $exercise_class, $choice ) {

            $($div_class).sortable({
                start: function( event, ui ) { 
                       $(ui.item).css("box-shadow", "4px 2px 4px gray");
                   }, 
                stop: function (event, ui) {
                    var valeurs = "";
                    $($exercise_class ).each(function() {
                        let parcours_id = $(this).attr("data-parcours_id"); 
                        valeurs = valeurs + parcours_id +"-";
                    });

                    $(ui.item).css("box-shadow",  "2px 1px 2px gray");

                    if ($choice) {
                        this_url =  "../../ajax/parcours_sorter"  ;                   
                    }
                    else
                         {
                        this_url =  "../../../ajax/parcours_sorter"   ;                  
                    }

                    $.ajax({
                            data:   { 'valeurs': valeurs    } ,   
                            type: "POST",
                            dataType: "json",
                            url: this_url,
                        }); 
                    }
                });

            }

        sorter_parcours('#evaluations_sortable',".evaluation_sorter",1) ;
        sorter_parcours('#parcours_sortable',".parcours_sorter",1) ;
        sorter_folders('#folders_sortable',".folder_sorter",1) ;

        sorter_parcours('#subparcours_sortable',".parcours_sorter",0) ;

        $('#course_sortable').sortable({
            start: function( event, ui ) { 
                   $(ui.item).css("box-shadow", "2px 1px 2px gray").css("background-color", "#271942").css("color", "#FFF"); 
               },
            stop: function (event, ui) {


                let parcours_id = $("#parcours_id").val();
                var valeurs = "";
                         
                $(".course_sort").each(function() {
                    let this_chapter_id = $(this).val();
                    valeurs = valeurs + this_chapter_id +"-";
                });


                $(ui.item).css("box-shadow", "0px 0px 0px transparent").css("background-color", "#dbcdf7").css("color", "#271942"); 

                $.ajax({
                        data:   { 'valeurs': valeurs , 'parcours_id' : parcours_id,  } ,   
                        type: "POST",
                        dataType: "json",
                        url: "../../ajax/course_sorter" 
                    }); 
                }
            });


        function sorter_folders($div_class , $exercise_class, $choice ) {

            $($div_class).sortable({
                start: function( event, ui ) { 
                       $(ui.item).css("box-shadow", "4px 2px 4px gray");
                   }, 
                stop: function (event, ui) {
                    var valeurs = "";
                    $($exercise_class ).each(function() {
                        let parcours_id = $(this).attr("data-parcours_id"); 
                        valeurs = valeurs + parcours_id +"-";
                    });
                    $(ui.item).css("box-shadow",  "2px 1px 2px gray");

    
                    this_url =  "../../ajax/folders_sorter"  ;                   
  
                    $.ajax({
                            data:   { 'valeurs': valeurs    } ,   
                            type: "POST",
                            dataType: "json",
                            url: this_url,
                        }); 
                    }
                });

            }


        // =================================================================================================================
        // =================================================================================================================           
        // ===========================================  mastering     ======================================================
        // ================================================================================================================= 
        // =================================================================================================================

        function sorter_mastering(param0, param1){

            $(param0).sortable({
            start: function( event, ui ) { 
                   $(ui.item).css("box-shadow", "2px 1px 2px gray").css("background-color", "#271942").css("color", "#FFF"); 
               },
            stop: function (event, ui) {


                let relationship_id = $("#relationship_to_mastering").val();
                var valeurs = "";
                         
                $(param1).each(function() {
                    let this_mastering_id =  $(this).attr("data-mastering_id"); 
                    valeurs = valeurs + this_mastering_id +"-";
                });

 
                $(ui.item).css("box-shadow", "0px 0px 0px transparent").css("background-color", "#dbcdf7").css("color", "#271942"); 

                $.ajax({
                        data:   { 'valeurs': valeurs , 'relationship_id' : relationship_id,  } ,   
                        type: "POST",
                        dataType: "json",
                        url: "../../ajax/sort_mastering" 
                    }); 
                }
            });
        }

        sorter_mastering("#layer4", "#layer4 .sorter_mastering") ;
        sorter_mastering("#layer3", "#layer3 .sorter_mastering") ;
        sorter_mastering("#layer2", "#layer2 .sorter_mastering") ;
        sorter_mastering("#layer1", "#layer1 .sorter_mastering") ;




        // =================================================================================================================
        // =================================================================================================================           
        // ===========================================  Les sections  ======================================================
        // ================================================================================================================= 
        // =================================================================================================================
        
         $('#create_section').submit(function(event) {

                    event.preventDefault();   

                    var formData = new FormData(this); 
                    let parcours_id = $('#parcours_id').val(); 
                    formData.append("parcours_id", parcours_id);
                    formData.append('attach_file', $('input[type=file]')[0].files[0]); 


                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                    formData.append("csrfmiddlewaretoken" , csrf_token);
 

                    $.ajax({
                        url: '../../ajax/create_title_parcours',
                        data: formData ,
                        type: "POST",
                        dataType: "json",
                        success: function (data) { 
                        $(data.html).insertBefore( $('#exercise_sortable').children()[0] );
                        },
                        cache: false,
                        contentType: false,
                        processData: false
                    });
                });

        $('body').on('click','.erase_title', function (){   
            let parcours_id = $(this).attr('data-parcours_id');  
            let exercise_id = $(this).attr('data-exercise_id');  
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

            if (!confirm('Vous souhaitez supprimer cette section/sous-section ?')) return false;

            $.ajax({
                url: '../../ajax/erase_title',
                data: {
                    'parcours_id': parcours_id,
                    'exercise_id': exercise_id,
                    csrfmiddlewaretoken: csrf_token,                        
                },
                type: "POST",
                dataType: "json",
                success: function (data) { 
                $("#new_title"+exercise_id).remove() ;
                }
            });
        });


        // ==================================================================================================================  
        // ==================================================================================================================             
        // ============================================       Signelements       ============================================ 
        // ================================================================================================================== 
        // ==================================================================================================================
 
            $('#form_error_set').hide();  
            $('#error_set').click(function(event) {
                     $('#form_error_set').toggle(500);  
                });


            $('#error_sender').on('click', function () {
                 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
              
                let message =  $("#message").val()  ;
                let exercise_id =  $(this).attr("data-exercise_id");  
                let parcours_id =  $(this).attr("data-parcours_id"); 
                let from =  $(this).attr("data-from");   

                if (message == "") { alert("Vous devez décrire brièvement le problème.") ; return false ; }    

                if (from == "0") { url_to ="../../ajax/exercise_error"} else  { url_to ="../ajax/exercise_error" ; } 
     
                $("#loader").html("<i class='fa fa-spinner fa-2x fa-pulse'></i>")  ;

                $.ajax({
                    url: url_to,
                    data: {
                        'message': message,
                        'exercise_id': exercise_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $(".verif_sender").addClass("verif_sender_sent");
                        $(".verif_sender").html(data.htmlg);
                        $("#loader").hide()  ;
                    }
                });
            });


 
            $('#form_peda_set').hide();  
            $('#peda_set').click(function(event) {
                     $('#form_peda_set').toggle(500);  
                });

 
            $('#form_peda_set_live').hide();  
            $('#peda_set_live').click(function(event) {
                     $('#form_peda_set_live').toggle(500);  
                });





            $('#sender_peda').on('click', function () {
                 
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
              
                let message =  $("#message_peda").val()  ;
                let exercise_id =  $(this).attr("data-exercise_id"); 
                let parcours_id =  $(this).attr("data-parcours_id"); 
                let from =  $(this).attr("data-from");   

                if (message == "") { alert("Décrire brièvement le problème pédagogique que vous rencontrez.") ; return false ; }    

                if (from == "0") { url_to ="../../ajax/exercise_error_peda"} else  { url_to ="../ajax/exercise_error_peda" ; } 
     
                $("#loader_peda").html("<i class='fa fa-spinner fa-2x fa-pulse'></i>")  ;

                $.ajax({
                    url: url_to,
                    data: {
                        'message': message,
                        'exercise_id': exercise_id,
                        'parcours_id': parcours_id,
                        csrfmiddlewaretoken: csrf_token,                        
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {

                        $(".verif_sender_peda").addClass("verif_sender_sent");
                        $(".verif_sender_peda").html(data.htmlg);
                        $("#loader_peda").hide()  ;
                    }
                });
            });

        // ==================================================================================================================  
        // ==================================================================================================================             
        // ============================================   Date limite des tasks  ============================================ 
        // ================================================================================================================== 
        // =================================================================================================================


            $("#task_date").hide(500);
            $("#publish_date").hide(500);

            function makeItemAppear($toggle, $item) {
                    $toggle.change(function () {
                        if ($toggle.is(":checked")) {
                            $item.show(500);
                        } else {
                            $item.hide(500);
                        }
                    });
                }

            function makeItemDisappear($toggle, $item) {
                    $toggle.change(function () {
                        if ($toggle.is(":checked")) {
                            $item.hide(500);
                        } else {
                            $item.show(500);
                        }
                    });
                }
            makeItemAppear($("#id_is_task"), $("#task_date"));
            makeItemDisappear($("#id_is_publish"), $("#publish_date"));




            // Affiche dans la modal la liste des élèves du groupe sélectionné
            $('.select_group').on('click', function (event) {
                let group_id = $(this).attr("data-group_id");
                let group_name = $(this).attr("data-group_name");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let from = $(this).attr("data-from");
                if (from == "0") { url_to ="../../../ajax/chargelisting"} else  { url_to ="../../ajax/chargelisting" ; } 
     
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'group_id': group_id,
                            'group_name': group_name,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: url_to ,
                        success: function (data) {
                            $('#modal_group_name').html(group_name);
                            $('#list_students').html(data.html_list_students);
                        }
                    }
                )
                });

            // Publie ou dépublie un exercice
            $('.action_content').on('click', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let statut = $(this).attr("data-statut");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let custom = $(this).attr("data-custom");
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            'statut': statut,
                            'custom': custom,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/publish" ,
                        success: function (data) {
                            $('#starter'+relationship_id).toggle();
                            $('#publisher'+relationship_id).attr("data-statut",data.statut);                  
                            $('#publisher'+relationship_id).html("").html(data.publish);
                            $('#publisher'+relationship_id).removeClass(data.noclass);
                            $('#publisher'+relationship_id).addClass(data.class);
                            $('#publisher'+relationship_id).removeClass(data.removeclass);
                        }
                    }
                )
                });   
        

               


            // valide si l'exercice est dans le calcul de la moyenne d'une section
            $('.select_average').on('click', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/average" ,
                        success: function (data) {                
                            $('#average'+relationship_id).removeClass(data.remove);
                            $('#average'+relationship_id).addClass(data.add);
                        }
                    }
                )
                });   
        






        // ==================================================================================================
        // ==================================================================================================
        // ============= Mutualisation de parcours
        // ==================================================================================================
        // ==================================================================================================

        function sharer_parcours($actionner,$target,$targetStatut, $is_folder){

                $actionner.on('click', function (event) {
                let parcours_id = $(this).attr("data-parcours_id");
                let statut = $(this).attr("data-statut");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                if( $is_folder) {  is_folder = "yes" ; } else { is_folder = "no" ; }
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'parcours_id': parcours_id,
                            'statut': statut,
                            'is_folder': is_folder,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "ajax_sharer_parcours" ,
                        success: function (data) {
                            $($target+parcours_id).attr("data-statut",data.statut);                  
                            $($targetStatut+parcours_id).removeClass(data.noclass);
                            $($targetStatut+parcours_id).addClass(data.class);
                            $($targetStatut+parcours_id).html("").html(data.label);
 
                        }
                    }
                )

                }); 
            } ;

            sharer_parcours( $('.parcours_sharer') , '#parcours_sharer' ,'#parcours_sharer_statut' , 0 ) ;
            sharer_parcours( $('.sharer') , '#folder_sharer' ,'#folder_sharer_statut' , 1 ) ;
        // ==================================================================================================
        // ==================================================================================================
        // ============= Publication de parcours
        // ==================================================================================================
        // ==================================================================================================

        function publisher_parcours($actionner,$target,$targetStatut, $is_folder){

                $actionner.on('click', function (event) {
                let parcours_id = $(this).attr("data-parcours_id");
                let statut = $(this).attr("data-statut");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let from = $(this).attr("data-from");


                if( $is_folder) {  is_folder = "yes" ; } else { is_folder = "no" ; }


                if( from == "2")  { url_from = "../../ajax/publish_parcours" ; } 
                else if (from == "0") {  url_from = "../../../ajax/publish_parcours" ;} 
                else  { url_from = "ajax/publish_parcours" ;} 


            

                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'parcours_id': parcours_id,
                            'statut': statut,
                            'from': from,
                            'is_folder': is_folder,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: url_from ,
                        success: function (data) {
                            $($target+parcours_id).attr("data-statut",data.statut);                  
                            $($targetStatut+parcours_id).removeClass(data.noclass);
                            $($targetStatut+parcours_id).addClass(data.class);
                            $($targetStatut+parcours_id).html("").html(data.label);

                            if( $is_folder) {  $('#is_publish_label'+parcours_id).html(data.is_publish_label); }

                            
                            if( from =="2" || from =="0") { 
                            $('.disc'+parcours_id).css("background-color",data.style); 
                            $('.disc'+parcours_id).css("background-color",data.style); 

                            if (data.statut == "true") {
                                $('#accueil_visible'+parcours_id).html("est"); 
                                $('#accueil_text_color'+parcours_id).removeClass("text-danger");  
                                $('#accueil_text_color'+parcours_id).addClass("text-success");
                            }
                            else {
                                $('#accueil_visible'+parcours_id).html("n'est pas");  
                                $('#accueil_text_color'+parcours_id).removeClass("text-success");  
                                $('#accueil_text_color'+parcours_id).addClass("text-danger");
                            }



                            }  
                        }
                    }
                )

                }); 
            } ;

            publisher_parcours( $('.publisher') , '#parcours_publisher' ,'#parcours_statut' , 0 ) ;
            publisher_parcours( $('.publisher') , '#folder_publisher' ,'#folder_statut' , 1 ) ;
 
        // ==================================================================================================
        // ==================================================================================================
        // ============= Affiche une fenetre modale personnalisée
        // ==================================================================================================
        // ==================================================================================================
            $(".card-dateur").hide();
            $(".card-skill").hide();

            function display_custom_modal($actionner,$target){
  
                $actionner.on('click', function (event) {
                    let relationship_id = $(this).attr("data-relationship_id");
                    $($target+relationship_id).toggle();
                    $($target+relationship_id).focus();
                });

            } ;

            display_custom_modal($('.action_task'),"#task_detail");
            display_custom_modal($('.select_task'),"#detail_dateur");
            display_custom_modal($('.select_publish'),"#detail_pub");
            display_custom_modal($('.select_details'),"#details");
            display_custom_modal($('.sharered'),"#share");
            display_custom_modal($('.select_skills'),"#skill");
            display_custom_modal($('.select_constraint'),"#detail_constraint");
            display_custom_modal($('.select_note'),"#select_note");

            display_custom_modal($('.select_task_close'),"#detail_dateur");
            display_custom_modal($('.select_publish_close'),"#detail_pub");
            display_custom_modal($('.select_details_close'),"#details");
            display_custom_modal($('.select_share_close'),"#share");
            display_custom_modal($('.select_skill_close'),"#skill");
            display_custom_modal($('.select_constraint_close'),"#detail_constraint");
            display_custom_modal($('.select_note_close'),"#select_note");

            display_custom_modal($('.select_div_group'),"#affectation"); 
            display_custom_modal($('.select_div_group_close'),"#affectation");

        // ==================================================================================================
        // ==================================================================================================
        // =============  Attribution des groupes depuis la liste des parcours
        // ==================================================================================================
        // ==================================================================================================


            $('.prcrs_selector').on('change', function (event) {

                let group_id = $(this).attr("data-group_id");
                let status = $(this).attr("data-status");
                let target_id = $(this).val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let checked = $(this).prop("checked") ;
                $("#loader"+group_id).html("<i class='fa fa-spinner'></i>") ;
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'checked': checked,
                            'group_id': group_id,
                            'status': status,
                            'target_id': target_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "ajax_affectation_to_group" ,
                        success: function (data) {

                            if ( status == "folder")
                                { $("#new_group_folder_affected"+target_id).html(data.html); }
                            else 
                                { $("#new_group_affected"+target_id).html(data.html); }

                            if ( data.change_link == "change")
                                { $("#this_folder"+target_id).hide(); }
                            else 
                                {$("#no_this_folder"+target_id).show();}


                            }  
                        }) 
                    });


                // Affiche dans la modal la liste des élèves du groupe sélectionné
                $('.actiontarget').on('click', function (event) {
                    let status = $(this).attr("data-status");
                    let target_id = $(this).attr("data-target_id");
                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                    $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            data: {
                                'status': status,
                                'target_id': target_id,
                                csrfmiddlewaretoken: csrf_token,
                            },
                            url: "ajax_charge_group_from_target",
                            success: function (data) {
                                $("#loader"+target_id).html("") ;
                                $('#modal_group_name').html(data.html_modal_group_name);
                                $('#list_students').html(data.html_list_students);
                            }
                        }
                    )
                });



        // ==================================================================================================
        // ==================================================================================================
        // =============  Notes
        // ==================================================================================================
        // ==================================================================================================
            $(".is_marked").hide() ;

            $('.details_notes').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let mark = $(this).val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            'mark': mark,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/notes" ,
                        success: function (data) {

                            $("#new_mark"+relationship_id).html("").html(mark);  
                            $("#new_mark"+relationship_id).show();
                            $('#is_marked'+relationship_id).show();
                            $("#no_new_mark"+relationship_id).hide(); 
                            }  
                        })
                    });


            $(".new_mark").hide() ;
            $('.no_marker').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/delete_notes" ,
                        success: function (data) {
               
                            $("#new_mark"+relationship_id).hide();
                            $("#no_new_mark"+relationship_id).html("").html("?");   
                            $("#no_new_mark"+relationship_id).show();   
                            $("#mark"+relationship_id).val("");           
                            }  
                        })
                    });



        // ==================================================================================================
        // ==================================================================================================
        // =============  Maxexo
        // ==================================================================================================
        // ==================================================================================================
 

            $('.maxexo').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let maxexo = $(this).val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            'maxexo': maxexo,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/maxexo" , 
                        })
                    });
 

        // ==================================================================================================
        // ==================================================================================================
        // =============  Constraint
        // ==================================================================================================
        // ==================================================================================================
            $(".save_constraint").hide(); // On cache la div pour interdire si le code n'est pas bon
            // ==================================================================================================
            // ==  Si tous est cliqué, le code devient all
            // ==================================================================================================
            $(".all_of_them").on('click', function () {  
                let relationship_id = $(this).attr("data-relationship_id");
                if ( $(this).is(":checked") )
                    {   
                        $("#codeExo"+relationship_id).val("all"); 
                        $("#save_constraint"+relationship_id).show(); 
                        $("#is_exist"+relationship_id).html("<i class='fa fa-check text-success'></i>");
                    }
                else 
                    {   
                        $("#codeExo"+relationship_id).val("");  
                        $("#save_constraint"+relationship_id).hide(); 
                        $("#is_exist"+relationship_id).html("");
                    }
                });


            // ==================================================================================================
            // ==  Vérifie qu'il existe un exercice avec ce code -> Permet l'enregistrement si succès
            // ==================================================================================================

            $(".codeExo").on('keyup', function () { 
                let codeExo = $(this).val();
                let relationship_id = $(this).attr("data-relationship_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                if (codeExo.length  == 8) { 
                                $.ajax({
                                    url: '../../ajax/infoExo',
                                    type: "POST",
                                    data: {
                                        'codeExo': codeExo,
                                        csrfmiddlewaretoken: csrf_token,    
                                    },
                                    dataType: 'json',
                                    success: function (data) {
                                        $("#is_exist"+relationship_id).html(data["html"]);

                                        if (data.test  == 1 )  { $("#save_constraint"+relationship_id).show();  }
                                        else { $("#save_constraint"+relationship_id).hide(); }
                                    }
                                });
                    }
                else {  $("#is_exist"+relationship_id).html(""); $("#save_constraint"+relationship_id).hide();  }
            });

            // ==================================================================================================
            // ==  Sauvegarde de la constrainte
            // ==================================================================================================

            $('.save_constraint').on('click', function (event) {  
                    let relationship_id = $(this).attr("data-relationship_id");
                    let parcours_id = $(this).attr("data-parcours_id");
                    let codeExo = $("#codeExo"+relationship_id).val();
                    let scoreMin = $("#scoreMin"+relationship_id).val();
                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                    $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            data: {
                                'relationship_id': relationship_id,
                                'parcours_id': parcours_id,                            
                                'codeExo': codeExo,
                                'scoreMin': scoreMin,
                                csrfmiddlewaretoken: csrf_token
                            },
                            url: "../../ajax/constraint_create" ,
                            success: function (data) {
                                if (data.all == 1) {   $("#new_constraint"+relationship_id).html("").html(data.html);   }
                                else { $("#new_constraint"+relationship_id).html(data.html); }
                                
                                $("#constraint"+relationship_id).removeClass("btn-danger");
                                $("#constraint"+relationship_id).addClass("btn-success");
                            }
                        }
                    ) 
                    });   
            // ==================================================================================================
            // ==  Sauvegarde de la constrainte
            // ==================================================================================================


            $('.delete_constraint').on('click', function (event) {
                    let constraint_id = $(this).attr("data-constraint_id");
                    let relationship_id = $(this).attr("data-relationship_id");
                    let is_all = $(this).attr("data-is_all");
                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                    $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            data: {
                                'relationship_id': relationship_id,
                                'constraint_id': constraint_id,
                                'is_all': is_all,                            
                                csrfmiddlewaretoken: csrf_token
                            },
                            url: "../../ajax/constraint_delete" ,
                            success: function (data) {
     
                                $("#new_constraint"+relationship_id + " #constraint_saving"+data.html).html(""); // Suppression de la ligne dans la div new_constraint

                                if (data.nbre == 0) { 
                                $("#constraint"+relationship_id).removeClass("btn-danger");
                                $("#constraint"+relationship_id).addClass("btn-default");
                                }



                            }
                        }
                    ) 
                    });  




        // ==================================================================================================
        // ==================================================================================================
        // =============  Skill
        // ==================================================================================================
        // ==================================================================================================

            $('.skill_selector').on('click', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let skill_id = $(this).val();

                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            'skill_id': skill_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/skills" ,
                    }
                )

                });    



        // ==================================================================================================
        // ==================================================================================================
        // =============  Copie le code, l'adresse d'un exercice
        // ==================================================================================================
        // ==================================================================================================
            $(".copy").on("click", function() {

                let custom = $(this).attr("data-custom");
                let parcours_id = $(this).attr("data-parcours_id");
                let exercise_id = $(this).attr("data-exercise_id");  
                let relationship_id = $(this).attr("data-relationship_id");  

                if (custom==1) {
                    if (alert("Pour coller dans une page, sélectionner et copier (CTRL+C) :                    https://sacado-academie.fr/qcm/write_custom_exercise/"+exercise_id+"/"+parcours_id)) ;
                        $("#custom_share"+exercise_id).hide();
                    }
                    else {
                    if (alert("Pour coller dans une page, sélectionner et copier (CTRL+C) :                    https://sacado-academie.fr/qcm/"+parcours_id+"/"+exercise_id+"/")) ;
                        $("#share"+relationship_id).hide();
                    }
                }
                );


            $(".copy_link").on("click", function() {
                let code = $(this).attr("data-code");
                alert("Double-cliquer sur le code suivant et copier (CTRL+C)  :  "+ code)
                });



        // ==================================================================================================
        // ==================================================================================================
        // =============  Date et détais relationship
        // ==================================================================================================
        // ==================================================================================================

            $('.dates').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let type = $(this).attr("data-type");
                let dateur = $(this).val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                $("#loading"+relationship_id).html("<i class='fa fa-spinner fa-pulse fa-fw'></i>");  
 
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            'dateur': dateur,
                            'type': type,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/dates" ,
                        success: function (data) {
                            $("#loading"+relationship_id).html("");  
                            if (type == 0)
                                { $('#starter'+relationship_id).val(data.dateur); $('#starter'+relationship_id).val(data.dateur);}
                            else
                                { $('#dateur'+relationship_id).val(data.dateur);
                                $('#pub_task'+relationship_id).html('').html(data.label); }              

                        }
                    }
                )

                });


            $('.dateur').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let type = $(this).attr("data-type");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let custom = $(this).attr("data-custom");

                $("#loading"+relationship_id).html("<i class='fa fa-spinner fa-pulse fa-fw'></i>"); 
                
                let dateur = $(this).val();
                    datas = {
                            'relationship_id': relationship_id,
                            'dateur': dateur,
                            'custom': custom,
                            'type': type,
                            csrfmiddlewaretoken: csrf_token
                        } ;

                $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            data: datas,
                            url: "../../ajax/dates" ,
                            success: function (data) {
                            $("#loading"+relationship_id).html("");  
                                if (type == 0)
                                    { $('#starter'+relationship_id).val(data.dateur); 
                                    $("#detail_pub"+relationship_id).hide();
                                    }
 

                                else 
                                    { $('#dateur'+relationship_id).val(data.dateur);
                                    $('#pub_task'+relationship_id).html('').html(data.dateur); 
                                    $('#pub_task'+relationship_id).addClass(data.class);
                                    $('#pub_task'+relationship_id).removeClass(data.noclass); 
                                    $("#detail_dateur"+relationship_id).hide();
                                } 

                            }
                        }
                    )
                    .done(function() {
                          $( this ).focus();
                        });

                });


            $('.details_relation').on('change', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let custom = $(this).attr("data-custom");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let situation = $("#situation"+relationship_id).val();

                let duration = $("#duration"+relationship_id).val();
                let type = $(this).attr("data-type"); 

                datas = {   'relationship_id': relationship_id,
                            'situation': situation,
                            'duration' : duration,
                            'custom' : custom,
                            'type' : type,
                            csrfmiddlewaretoken: csrf_token,
                        } ;

 

                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: datas,
                        url: "../../ajax/dates" ,
                        success: function (data) {

                            if (data.clock) {
                                $('#clock'+relationship_id).html("").html(data.clock); 
                                $('#duration'+relationship_id).val(duration);                                 
                            }
                            if (data.save) {
                                $('#save'+relationship_id).html("").html(data.save);
                                $('#situation'+relationship_id).val(situation);
                            }
                            else if (data.annoncement) { 
                                $('#annoncement'+relationship_id).html("").html(data.annonce); 
                            }
  
                        }
                    }
                )
                });

        // ==================================================================================================================  
        // ==================================================================================================================             
        // ====================================================   Flex page  === ============================================ 
        // ================================================================================================================== 
        // ==================================================================================================================  


            var flex_size = 0;
            $('#buttonToggle').on('click', function () {

                        if ( flex_size%2 == 0)
                            {
                            $('#sub_menu_left').css("display","none")
                            $('#flex').attr("class","col-xs-12 col-md-12")
                            if ($('#sub_menu_left')) 
                                {$('#inside_flex').css("padding","20px") ;}

                            $('#buttonToggle').css("color","orange") ;

                            }
                        else
                           {
                            $('#sub_menu_left').css("display","block")
                            $('#flex').attr("class","col-xs-12 col-md-10")
                            if ($('#sub_menu_left')) 
                                {$('#inside_flex').css("padding","0px") ;}

                            $('#buttonToggle').css("color","#309ae4") ;
                            } 
                            flex_size ++;
                        });

        // ==================================================================================================================  
        // ==================================================================================================================             
        // ================================= Choix sans Audio de Remédiation ================================================ 
        // =========================   La partie audio est traité par recorder_voice.js   =================================== 
        // ==================================================================================================================  
 
            $('.remediation').on('click', function (event) {
                let relationship_id = $(this).attr("data-relationship_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                var li_dom = document.querySelector("#recordingsList > li")
                if (li_dom) { li_dom.remove() ; $("#formats").html("");}

                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'relationship_id': relationship_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/remediation" ,
                        success: function (data) {
                            $('#remediation_form').html('').html(data.html); 
                            $('#id_relationship').val(relationship_id); 
                        }
                    }
                )
            });

 
            $('.remediationCustom').on('click', function (event) {

                let parcours_id = $(this).attr("data-parcours_id");
                let customexercise_id = $(this).attr("data-customexercise_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();

                var li_dom = document.querySelector("#recordingsList > li")
                if (li_dom) { li_dom.remove() ; $("#formats").html("");}

                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'parcours_id': parcours_id,
                            'customexercise_id': customexercise_id,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: "../../ajax/remediation" ,
                        success: function (data) {
                            $('#remediation_form').html('').html(data.html); 
                            $('#id_relationship').val(customexercise_id); 
                        }
                    }
                )
            });


        // ==================================================================================================================  
        // ==================================================================================================================             
        // ====================================================   fenetre modale ============================================ 
        // ================================================================================================================== 
        // ================================================================================================================== 
 
            $('.remediation_viewer').on('click', function (event) {
                let remediation_id = $(this).attr("data-remediation_id");
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                let url_code = $(this).attr("data-url");
                let is_custom = $(this).attr("data-is_custom");

                console.log(is_custom) ; 

                if (url_code == "0") {url = "../../ajax/remediation_viewer" ;}
                else if (url_code == "1") {url = "../ajax/remediation_viewer" ;}


                $("#loader_shower").html("<i class='fa fa-spinner fa-pulse fa-fw fa-3x'></i>");  
                $.ajax(
                    {
                        type: "POST",
                        dataType: "json",
                        data: {
                            'remediation_id': remediation_id,
                            'is_custom': is_custom,
                            csrfmiddlewaretoken: csrf_token
                        },
                        url: url ,
                        success: function (data) {
                            $('#remediation_shower').html('').html(data.html);          
                        }
                    }
                )

                });

        // ====================================================================================================================
        // ====================================================================================================================
        // =========================================    renewal school fee   ================================================== 
        // ====================================================================================================================
        // ====================================================================================================================


 
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

    });        
});