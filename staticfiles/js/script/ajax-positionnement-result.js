define(['jquery',  'bootstrap' ,  'chart' ], function ($) {
    $(document).ready(function () {
 
 
        console.log(" ajax-positionnement-result chargé ");
    
        labels  = $("#labels").val().split("____") ;
        dataset = $("#dataset").val().split("____")  ;
        seuils = []
        for (var i=0;i<labels.length;i++){
            seuils.push(80)
        }


        var ctx = $("#chart-line");
        var myLineChart = new Chart(ctx, {
            type: 'radar',
            options: {
                maintainAspectRatio: false,
                scale: {
                    ticks: {
                        beginAtZero: true,
                        max: 100,
                        min: 0,
                    }
                }
            },
            data: {
                labels: labels ,
                datasets: [{
                    data: dataset,
                    label: "Mes scores",
                    borderWidth: 2,
                    borderColor: "rgba(93,67,145,1)",
                    backgroundColor: 'rgba(93,67,145,0.1)',
                },{
                    data: seuils,
                    label: "Seuils",
                    borderColor: "rgba(98,216,90,1)",
                    backgroundColor: 'rgba(98,216,90,0.1)',
                    borderWidth: 1,
                }]
            },
        });

 
    });
});