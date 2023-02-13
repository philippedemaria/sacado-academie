define(['jquery', 'bootstrap', 'ui'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_axe.js  OKK");

 

//*************************************************************************************************************  
// Classement sur axe
//*************************************************************************************************************  
var div_width = $('#body_zone_exercise').width() ;
var offsetWidth = Math.floor(div_width)-220;
$('#body_zone_exercise').width() ;

var nb_tableaux=document.getElementsByClassName("tableau").length; // Nb de situations



    $( document ).on('mouseover', ".carte" , function () { 
        var loop = $(this).data('loop');
        $( this ).draggable({
                containment: ".dropzone"+loop ,
                start: function() {
                    offsetTop = $(this)[0].offsetTop ; 
                    carte_id = $(this).attr('id')  ;
                    var verticale = $("<div></div>");
                    verticale.attr('id','this_card_position'+carte_id);
                    verticale.css('position',"absolute");
                    verticale.css('top'    , 70 - offsetTop);
                    verticale.css('height' , offsetTop - 70);
                    verticale.css('left'   , 75) ;
                    verticale.css('background','#b295ff');
                    verticale.css('border', '1px solid #b295ff');
                    $(this).append(verticale);

                },
                drag: function() {
                    offsetTop = $(this)[0].offsetTop ;                
                    carte_id = $(this).attr('id')  ;
                    verticale = $('#this_card_position'+carte_id);                    
                    verticale.css('top'    , 70 - $(this)[0].offsetTop);
                    verticale.css('height' , $(this)[0].offsetTop - 70);
                    verticale.css('left'   , 75) ;
                    verticale.css('background','#b295ff');
                    verticale.css('border', '1px solid #b295ff');
                    $(this).append(verticale);
                },

          });

        $( ".dropzone"+loop ).droppable({
                drop: function( event, ui ) {
 
                    offsetLeft = $(ui.draggable[0])[0].offsetLeft ;
                    this_identifiant = $(ui.draggable[0]).data("identifiant") ;
                    $("#abscisse"+this_identifiant).val(offsetLeft);
                },

        });

    })



            for (var index = 0; index < nb_tableaux ; index++ ){ 

                        $('#axe'+index).css('width',offsetWidth+"px") ;
                        $('#width_axe'+index).val(offsetWidth) ;

                        var xmin      = parseFloat($("#xmin"+index).val().replace(",",".")); 
                        var xmax      = parseFloat($("#xmax"+index).val().replace(",","."));
                        var tick      = parseFloat($("#tick"+index).val().replace(",","."));
                        var subtick   = parseFloat($("#subtick"+index).val().replace(",","."));

                        var tab       = document.getElementById("tableau"+index);
                        var yoffset   = tab.offsetTop;
                        var xoffset   = tab.offsetLeft+75;            
                        var topz      = $(".loop0").length ;   // le niveau de la couche la plus haute

                        var axe = document.getElementById("axe"+index);
                          //dessin des graduations de l'axe
             

                        function placeValeur(x,v) {     
                           // position en pixels, en fonction de la valeur x
                           x_axe=Math.round((x - xmin )/( xmax - xmin ) * offsetWidth) ; 

                           // creation du label : le texte de la valeur à afficher
                           if (v){ 
                           label=document.createElement("div");
                           label.textContent=x.toString();
                           label.style.position="absolute";
                           label.style.top  = "-40px";
                           axe.appendChild(label);
                           label.style.text_align="center";
                           label.style.left = x_axe-label.offsetWidth/2+"px";
                            }
                           // le "tick" = la graduation 
                           let tick= document.createElement("div");
                           tick.style.position="absolute";
                           tick.style.background='#5f8cff';
                            if (v)
                                {
                                    tick.style.top  = '-10px' ;
                                    tick.style.height= '12px' ;
                                }
                            else {
                                    tick.style.top  = '-5px' ;
                                    tick.style.height= '7px' ;
                            }


                           tick.style.width="0px";
                           tick.style.border="1px solid #5f8cff";
                           tick.style.left = x_axe+"px";
                           axe.appendChild(tick); 
                        }

                        function dessineGraduations(){

                            for (var x = xmin ; x < xmax ; x = x + tick ) 
                                { 
                                placeValeur(x,1) 
                            }
                            for (var x = xmin ; x < xmax ; x = x + 1/subtick ) 
                                { 
                                placeValeur(x,0) 
                            }

                            placeValeur( xmax ,1);
                        }

                        dessineGraduations();

                        cartes=Array();
                        var xcarte=Array()
                        var ycarte=Array()

                        for (i=0;i< topz ;i++) {  

                            c = document.getElementById("carte"+index +"_"+i.toString()); 
                            c.style.top    = 140+yoffset + (i)*50 + "px";
                            c.style.left   = xoffset + (i)*50 + "px";
                            c.style.zIndex = i ;
                            cartes.push(c);
                            AssociationEvnt(cartes[i]);
                        }


                        function AssociationEvnt(carte) {
                          var X=0, Y=0,dernierX = 0, dernierY = 0;
                          carte.onmousedown = (e) => dragMouseDown(carte,e);
                          //carte.onmouseout  =  (e)=> closeDragElement(carte)
                          // clic droit : on détache la carte de l'axe
                          carte.oncontextmenu = (e)=> {
                               if (carte.childNodes.length>=3) {carte.removeChild(carte.childNodes[2])}
                               carte.childNodes[1].innerHTML="";
                           }
                        }

            }







            $(document).on('click', ".show_axe_correction" , function (event) {
         

                    let loop           = $(this).data("loop") ;
                    event.preventDefault();   
                    my_form = document.querySelector("#all_types_form");
                    var form_data = new FormData(my_form); 
         
                    let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
                    let supportfile_id = $(this).data("supportfile_id") ;

                    form_data.append("supportfile_id" , supportfile_id); 
                    form_data.append("loop" , loop); 
                    form_data.append("csrfmiddlewaretoken" , csrf_token); 

                    $.ajax(
                        {
                            type: "POST",
                            dataType: "json",
                            traditional : true,
                            data: form_data,
                            url: "../../check_axe_answers",
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

 
