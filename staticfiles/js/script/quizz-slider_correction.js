define(['jquery',  'bootstrap' ], function ($) {
    $(document).ready(function () {

        console.log(" quizz-slider_correction chargé ");

        var slideBox = $('.slider ul'),
            slideWidth = 1000 ,
            slideQuantity = $('.slider ul').children('li').length,
            currentSlide = 1 ,
            currentQuestion = 1 ;

        slideBox.css('width', slideWidth*slideQuantity);

     
        function transition(currentSlideInput, slideWidthInput){

            var pxValue = -(currentSlideInput -1) * slideWidthInput ; 
            slideBox.animate({
                'left' : pxValue
            })
            this_question = parseInt( (currentSlideInput+1)/2)-1 ;

            $(".this_question").addClass("btn-default").removeClass("btn-primary") ;
            $("#question"+this_question).removeClass("btn-default").addClass("btn-primary") ;
        }

//======================================================================================================
//====================== Vue en plein écran
//======================================================================================================
        $("#stop_quizz").hide();
        // fermer le plein écran
        $('#stop_quizz').on('click', function(){ 

            $("#content_title_page").show(500);
            $("#navbarLeft").show(500);
            $("#stop_quizz").hide(500);
            $("#starter_quizz").show(500);
            document.fullScreenElement && null !== document.fullScreenElement || !document.mozFullScreen && !document.webkitIsFullScreen ? document.documentElement.requestFullScreen ? document.documentElement.requestFullScreen() : document.documentElement.mozRequestFullScreen ? document.documentElement.mozRequestFullScreen() : document.documentElement.webkitRequestFullScreen && document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT) : document.cancelFullScreen ? document.cancelFullScreen() : document.mozCancelFullScreen ? document.mozCancelFullScreen() : document.webkitCancelFullScreen && document.webkitCancelFullScreen()
       
        });
        // Vue en plein écran
        $('#starter_quizz').on('click', function(){ 

            $("#content_title_page").hide(500);
            $("#navbarLeft").hide(500);
            $("#stop_quizz").show(500);
            $("#starter_quizz").hide(500);
            document.fullScreenElement && null !== document.fullScreenElement || !document.mozFullScreen && !document.webkitIsFullScreen ? document.documentElement.requestFullScreen ? document.documentElement.requestFullScreen() : document.documentElement.mozRequestFullScreen ? document.documentElement.mozRequestFullScreen() : document.documentElement.webkitRequestFullScreen && document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT) : document.cancelFullScreen ? document.cancelFullScreen() : document.mozCancelFullScreen ? document.mozCancelFullScreen() : document.webkitCancelFullScreen && document.webkitCancelFullScreen()
       
       });
//======================================================================================================
//======================  
//======================================================================================================


       $('.nav').on('click', function(){ 

        $(".instruction").hide();
        $(".starter_in").hide();

               var whichButton = $(this).data('nav'); 

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


                var starter_play = 0 ,
                    step         = 0 ,
                    now          = 0 ,
                    step_count   = 0;

                $('#start_quizz').on('click', function(){

                        $(".instruction").show();
                        $(".starter_in").show();
                        this_slide = parseInt( (currentSlide-1)/2) ; 
                        these_slide = 1+parseInt( (currentSlide-1)/2) ; 

                        if ( starter_play%2 === 0 ) {
                            $("#start_quizz").html("").html("<button  class='btn btn-danger'><i class='fa fa-stop'></i> Arrêter</button>") ;
                            if( $("#stoper_quizz") ) { $("#stoper_quizz").attr("id","#counterdown"+this_slide); }
                            if( $("#stoper_introduction") ) { $("#stoper_quizz").attr("id","#counterdown"+these_slide); }
                            auto_play() ;                         
                        }
                        else // arret du compteur
                        {  
                            $("#start_quizz").html("").html("<button  class='btn btn-default'><i class='fa fa-play'></i> Démarrer</button>") ;
                            $("#counterdown"+this_slide).attr("id","stoper_quizz");
                            $("#countdown"+these_slide).attr("id","stoper_introduction");
                        }

                        starter_play++ ;
                })  
 

                    function timer(cible , this_slide , duree  ){
                                
                        var interval = setInterval(function() {
                            duree = duree - 1000;
                            document.getElementById(cible+this_slide).textContent = duree/1000;

                            // Changement de la couleur selon le temps restant
                            if (duree <= 10000) { $("#"+cible+this_slide).addClass("countdownOrange") ; }
                            if (duree <= 5000) { $("#"+cible+this_slide).removeClass("countdownOrange").addClass("countdownRed") ; }
                            if (duree <= 0) { auto_play() ; clearInterval(interval); }

                        }, 1000)


                            var pxValue = - (currentSlide -1) * slideWidth ; // décalage pour l'animation du slide.
                            slideBox.animate({'left' : pxValue});            // Animation du slide.                        
                    }



                    function auto_play(){


                            if (currentSlide === slideQuantity) // Si on arrive au bout du nombre de slides, le quizz s'arrete.
                                { 
                                    $("#start_quizz").html("").html("<button  class='btn btn-default'><i class='fa fa-play'></i> Démarrer</button>") ;
                                    clearInterval(interval);
                                    $("#content_title_page").show(500);
                                }
                            else  // Si on avance d'une slide à chaque fois.
                                { 
                                    currentSlide++ ;
                                }




                            $(".thisquestion").removeClass("btn-primary").addClass("btn-default")  ;   // Couleurs des boutons

                            if ( step === 0 )  // Introduction du quizz
                            {
                                this_slide =  0 ; 
                                duree = $("#inter_slide1").val() * 1000 ;
                                $("#question1").addClass("btn-primary").removeClass("btn-default")  ;    // Couleurs des boutons
                                timer("countdown" , 1 , duree  )

                            }
                            else  // Lecture des diapo des questions
                            {

                                if (this_slide === 0 ) {this_slide++;}

                                //this_slide = parseInt( (currentSlide-1)/2) ; // Sélection du temps entre les diapos ou de la diapo

                                if ( step%3 === 0 ) 
                                    {
                                        this_slide++;
                                        duree = $("#inter_slide"+this_slide).val() * 1000 ;
                                        timer("countdown" , this_slide , duree );
                                    }
                                else if ( step%3 === 1 )  
                                    {   
                                        duree = $("#duration"+this_slide).val() * 1000 ;
                                        timer("counterdown" , this_slide , duree  )
                                    }

                                else
                                    { 
                                        duree = $("#answer_choice"+this_slide).val() * 1000 ;
                                        timer("counterdown_cor" , this_slide , duree  );  
                                    }

                                 // Couleurs des boutons déjà des questions déjà travaillées
                                currentQuestion++ ; 
                                this_question = parseInt( (currentQuestion+1)/2) ;
                                for (col=1;col<this_question;col++){ $("#question"+col).addClass("btn-success").removeClass("btn-default")  ;  }
                                 // Seule la question en cours en bleu
                                $("#question"+this_question).addClass("btn-primary").removeClass("btn-default")  ;  
                            }

                            step++ ;
 
                    }


    });
});