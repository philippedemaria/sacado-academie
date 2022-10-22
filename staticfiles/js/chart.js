define(['jquery','bootstrap_popover', 'bootstrap','chart'], function ($) {
$(document).ready(function () {
 
 
        console.log("---- NEW test ajax-accueil.js ---") ;  

 

         // *************************************************************
        // chart.js
        // *************************************************************
        var marksCanvas   = document.getElementById("marksChart");
        var scoreswRadar  = document.getElementById("scoreswRadar").value;
        var waitingsRadar = document.getElementById("waitingsRadar").value;

        var liste_score_w_n = [] ; 
        var colors = [  "rgb(245,127,241,0.6)", 
                        "rgb(175,142,252,0.6)", 
                        "rgb(252,127,150,0.6)", 
                        "rgb(142,215,252,0.6)", 
                        "rgb(142,252,171,0.6)", 
                        "rgb(215,252,142,0.6)", 
                        "rgb(252,243,142,0.6)", 
                        "rgb(252,191,142,0.6)", 

                        "rgb(92,70,143,0.6)", 
                        "rgb(143,90,70,0.6)",
                        "rgb(70,143,90,0.6)", 
                        "rgb(90,143,70,0.6)",
                        "rgb(143,70,90,0.6)",
                        "rgb(70,90,143,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)",
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)",
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)", 
                        "rgb(245,127,197,0.6)",
        ]


        var liste_colors = [] ; 
        liste_score_w = scoreswRadar.split("-");

        liste_score_w.forEach( (item,index) =>{ 
            item_int = parseInt(item);
            if (!isNaN(item_int))
                {
                    liste_score_w_n.push(item_int);
                    liste_colors.push(colors[index]);
                }
        });


        var marksData = {
            labels: waitingsRadar.split("-") ,
            datasets: [{
                label : "Attendus",
                backgroundColor: liste_colors,
                data:  liste_score_w_n,
            }]
        };

        var radarChart = new Chart(marksCanvas, {
                              type: 'polarArea',
                              data: marksData,
                              options: {
                                responsive: true,
                                plugins: {
                                  legend: {
                                    display: false,
                                  },
                                }
                              },
                            } );





        var barChart = document.getElementById("barChart");
        var scoresbarSet = document.getElementById("scoresbarSet").value;
        var datebar      = document.getElementById("datebarSet").value;

        var liste_score_b_n = [] ; 
        liste_score_b = scoresbarSet.split("-");
        liste_score_b.forEach( (item) =>{ 
            item_int = parseInt(item);
            if (!isNaN(item_int))
                {liste_score_b_n.push(item_int);}
        });

 

        var marksDatas = {
            labels: ["Non acquis", "En cours", "A renforcer", "Acquis"],
            datasets: [{
                label : datebar ,
                backgroundColor: ["rgb(254,176,169,0.6)", "rgb(254,244,176,0.6)","rgb(130,197,181,0.6)","rgb(41,153,126,0.6)"],
                data: liste_score_b_n,
                    }] ,           
                options: {
                    responsive: true,
                    label: { display: false }, 
                    title: {display: false},
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
            },

        };

        var radarChart = new Chart(barChart, {
          type: 'bar',
          data: marksDatas,
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: false,
              },
            }
          },
        });

        // *************************************************************
        // *************************************************************
        // *************************************************************



    });
});
 
