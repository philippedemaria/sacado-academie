define(['jquery', 'bootstrap','moment', 'fullcalendar'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS  display_calendar_teacher.js OK");
 


		$(".calendar").fullCalendar({
			defaultView: 'agendaWeek',
			aspectRatio: 1.5,
	        header: {
	                  left: 'prev,next today',
	                  center: 'title',
	                  right: 'month,agendaWeek,agendaDay'
	          		},

			editable: false,
	     	selectable: false,
	     	selectHelper: false,
			eventLimit : false,
			eventStartEditable : false, 
			monthNames: ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet',
	                  'Août','Septembre','Octobre','Novembre','Décembre'],
	        monthNamesShort: ['Janv.','Févr.','Mars','Avr.','Mai','Juin','Juil.','Août','Sept.','Oct.','Nov.','Déc.'],
	        dayNames: ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'],
	        dayNamesShort: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
	        firstDay:1, // Lundi premier jour de la semaine
	        buttonText: {
	              today:    'Aujourd\'hui',
	              month:    'Mois',
	              week:     'Semaine',
	              day:      'Jour'
	          },
			events: '../events_my_teacher/'+ $("#my_teacher_id").val(),	                  
 

			eventClick: function(event, element) { 
				$("#new_event").modal('show'); 

				$("#id_start").val(event.start.format("HH:mm"));  
				$("#id_date").val(event.start.format("YYYY-MM-DD"));
				$("#id_real_date").val(event.start.format("DD MMM YYYY"));
				$("#id_real_start").val(event.start.format("HH:mm"));  


			  }

		}) ;


				
	}); 

})

			
           