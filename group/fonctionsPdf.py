from django.conf import settings # récupération de variables globales du settings.py
from account.models import Student, Teacher, User, Resultknowledge, Resultlastskill, Resultskill
from socle.models import Knowledge, Theme, Level, Skill
from qcm.models import Exercise, Parcours, Relationship, Studentanswer, Resultexercise , Resultggbskill, Customexercise , Tracker
from django.db.models import Avg, Count, Min, Sum

############### bibliothèques pour les impressions pdf  #########################
import os
from io import BytesIO, StringIO
from django.core.mail import EmailMessage

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape , letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image , PageBreak,Frame , PageTemplate
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, red, black, white, blue , Color
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.axes import XCategoryAxis,YValueAxis
from reportlab.graphics.shapes import Drawing,Rect,String,Line

from textwrap import TextWrapper
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
cm = 2.54
#################################################################################

from datetime import datetime, date , timedelta
from general_fonctions import convert_seconds_in_time
from math import sin,cos



def radar(L):

    """dessine le radar d'une liste de listes [intitulé, note/100]
    valeur de retour : une "shape" de type Drawing
    """
    #print("radar : ",L)
    from reportlab.lib.units import cm
    
    haut=18*cm   #hauteur et largeur du rectangle encadrant
    larg=18*cm
    rayon=6*cm   #rayon du radar
    n=len(L)
    dangle=6.2832/n  #angle d'un secteur angulaire
    angle=1.5707   #angle de départ : pi/2 (verticale)
    deno=100  #note sur ?
    tick=10   #graduation tous les ?
    #cfond=Color(1,1,1) #couleur du fond
    cgrille=Color(0.8,0.8,0.8)  #couleur de la grille
    cligne=Color(1,0,0)         #couleur des la ligne des données
    w=TextWrapper(width=20)     #les intitules auront au plus 20 caractères
                                #de large, on les decoupe sur plusieurs lignes

    #-------------------------------------------------
    d=Drawing(larg,haut)
    d.add(String(larg/2,haut-0.5*cm,"Graphique des attendus", textAnchor="middle"))
    if n<=2 :  
        d.add(String(larg/2,haut/2,"pas assez de notes pour le graphique", textAnchor="middle"))
        return d
    
    for i in range(n) :
        a=angle+i*dangle
        # ----------- placement des intitulés
        intitule=Label()
        intitule.setOrigin(larg/2+(rayon+0.2*cm)*cos(a),haut/2+(rayon+0.2*cm)*sin(a))
        if 0.78 <(a % 6.28) <2.35 : 
            intitule.boxAnchor="s"
        elif 2.35 <= (a % 6.28) <3.92 : 
            intitule.boxAnchor="e"
        elif  3.92<=a % 6.28<5.5 :
            intitule.boxAnchor="n"
        else :
            intitule.boxAnchor="w"
        intitule.setText(w.fill(L[i][0]))
        d.add(intitule)
        #-------------------- la grille du radar
        d.add(Line(larg/2,haut/2,larg/2+rayon*cos(a),haut/2+rayon*sin(a), strokeColor=cgrille))
        for j in range(1,int(deno/tick)+1):
            r=rayon*j*tick/deno
            d.add(Line(larg/2+r*cos(angle+i*dangle),haut/2+r*sin(angle+i*dangle),\
                       larg/2+r*cos(angle+(i+1)*dangle),haut/2+r*sin(angle+(i+1)*dangle),\
                       strokeColor=cgrille ))

        #--------------------- la ligne des données  
        r1=L[i-1][1]*rayon/deno
        r2=L[i % n][1]*rayon/deno
        d.add(Line(larg/2+r1*cos(a),haut/2+r1*sin(a),larg/2+r2*cos(a+dangle),haut/2+r2*sin(a+dangle),\
                   strokeColor=cligne, strokeWidth=2))

    #------------------------ graduations
    
    for i in range(1,int(deno/tick)+1):
        r=rayon*(i-0.3)*tick/deno
        d.add(String(larg/2+r*cos(angle),haut/2+r*sin(angle),str(i*tick)))     
    return d


def diagBaton(data) :
    d = Drawing(400, 200)
    
    # code to produce the above chart
    bc = VerticalBarChart()
    couleurs=[[Color(0.95,0.95,0.95),Color(0.8,0.3,0.3) ], #non acquis
    [Color(0.95,0.95,0.95),Color(0.7,0.2,0.6) ],          #en cours
    [Color(0.95,0.95,0.95),Color(0.5,0.7,0.5) ],
    [Color(0.95,0.95,0.95),Color(0.2,0.2,0.8) ]]
    
    bc.x = 50
    bc.y = 10
    bc.height = 105
    bc.width = 300
    bc.data = data
    for i in range(len(data[0])):
        for j in range(len(data)):
            bc.bars[(j,i)].fillColor=couleurs[i%4][j%2]
    bc.strokeColor = black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 10
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = ['Non acquis', 'En cours ', 'Acquis', 'Expert']
    d.add(bc)
    return d
  
  
  
def pdfPeriode2(student, date_start,date_stop):
	"""rend les elements reportlab d'un pdf qui synthetise les résultats de l'elève student entre les deux dates"""
	
	elements = []
	sacado = ParagraphStyle('sacado', 
							fontSize=20, 
							leading=26,
							borderPadding = 0,
							alignment= TA_CENTER,
							)
	title = ParagraphStyle('title', 
							fontSize=20, 
							textColor=colors.HexColor("#00819f"),
							)
	subtitle = ParagraphStyle('title', 
							fontSize=16, 
							textColor=colors.HexColor("#00819f"),
							)
	normal = ParagraphStyle(name='Normal',fontSize=12,)	
	style_cell = TableStyle(
			[
				('SPAN', (0, 1), (1, 1)),
				('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
			]
		)



	logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
	logo_tab = [[logo, "SACADO Académie\nBilan des acquisitions" ]]
	logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
	logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
	elements.append(logo_tab_tab)
	elements.append(Spacer(0, 0.1*inch))

	studentanswers = student.answers.filter(date__lte = date_stop , date__gte= date_start)

	studentanswer_ids = studentanswers.values_list("exercise_id",flat=True).distinct() 

	nb_exo = studentanswer_ids.count() # Nombre d'exercices traités
	info = studentanswers.aggregate( duration =  Sum("secondes"), score =  Sum("point"), avg =  Avg("point"))
	scores = studentanswers.values_list("point",flat=True).order_by("point")
 
	score , duration , average_score = 0  , 0 , 0
	if info["score"]:
		score = info["score"]
	if info["duration"]:
		duration = info["duration"]
	if info["avg"]:
		average_score = int(info["avg"])


	k_ids = studentanswers.values_list("exercise__knowledge_id", flat=True).distinct()
	nb_k_p = k_ids.count()

	exo_ids = studentanswers.values_list("exercise_id", flat=True).distinct()
	nb_e = exo_ids.count()

	skill_ids = studentanswers.values_list("exercise__supportfile__skills", flat=True).distinct()
	nb_skills = skill_ids.count()

	theme_ids = studentanswers.values_list("exercise__theme_id", flat=True).distinct()

	##########################################################################
	#### Gestion des labels à afficher
	##########################################################################
	labels = [(student.user.first_name+" "+student.user.last_name).title(), 
	          "Classe de "+str(student.level),
	          "Du "+date_start.strftime("%d/%m/%y")+" au "+date_stop.strftime("%d/%m/%y"),
	          "Temps de connexion : "+convert_seconds_in_time(duration), "Score moyen : "+str(average_score)+"%" , \
			  "Exercices SACADO travaillés : " +str(nb_e)]
	spacers , titles,subtitles = [1],[0],[]

	i = 0
	for label in labels :
		if i in spacers : 
			height = 0.25
		else :
			height = 0.1
		if i in titles : 
			style = title
			height = 0.15
		elif i in subtitles :
			style = subtitle
			height = 0.1
		else :
			style = normal
		paragraph = Paragraph( label , style )
		elements.append(paragraph)
		elements.append(Spacer(0, height*inch))
		i+=1   

 
	##########################################################################
	#### Gestion des themes
	##########################################################################
	elements.append(Spacer(0, 0.25*inch))

	e_tab, bgc_tab = [] , [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]
	w_tab = [] 
	bgc = 0  

	paragraphexo = Paragraph( "Résultats des exercices : " , title )
	elements.append(paragraphexo)
	elements.append(Spacer(0, 0.15*inch))

	studentanswer_orders = studentanswers.prefetch_related('exercise') 

	exo_dict		  = dict()
	exo_intitule_dict = dict()
	waitings_exo_dict = dict()
	waitings_intitule_dict = dict()

	for studentanswer  in studentanswer_orders :
		if  studentanswer.exercise.id in exo_dict :
			exo_dict[studentanswer.exercise.id].append(studentanswer.point)
		else :
			exo_dict[studentanswer.exercise.id] = [studentanswer.point]
			exo_intitule_dict[studentanswer.exercise.id] =  studentanswer.exercise.supportfile.title
		w_id = studentanswer.exercise.knowledge.waiting.id	
		if  w_id in waitings_exo_dict :
			waitings_exo_dict[w_id].append(studentanswer.point)
		else :
			waitings_exo_dict[w_id] = [studentanswer.point]
			waitings_intitule_dict[w_id] = studentanswer.exercise.knowledge.waiting.name   


	bgc_tab.append(  ('BACKGROUND', (0,bgc), (-1,bgc), colors.Color(0,0.5,0.62))  )

	for k,vs in exo_dict.items() :
		chn = ""
		for v in vs : 
			chn += str(v)+"%  "
		e_tab.append( (exo_intitule_dict[k], chn ) )

	liste_radar = []
	try :
		for n,ws in waitings_exo_dict.items() :
			liste_radar.append( [ waitings_intitule_dict[n], sum(ws)/len(ws) ] )
	except :
		pass

	if len(e_tab) > 0 :
		e_tab_tab = Table(e_tab, hAlign='LEFT', colWidths=[5.5*inch,1.8*inch])
		e_tab_tab.setStyle(TableStyle([
					   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
					   ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
					   ]))	
		elements.append(e_tab_tab)
	else :
		elements.append(Paragraph("Aucune donnée",normal))
		elements.append(Spacer(0, 0.5*inch))

	if len(liste_radar) >=3  :
		d = radar(liste_radar)
		elements.append(d)
	else :
		elements.append(Spacer(0,0.3*inch))            
		if len(liste_radar)==0 :
			elements.append(Paragraph("Graphique des attendus : aucune donnée",normal))
		else :
			elements.append(Paragraph("Pas assez d'attendus pour dessiner un radar.",normal))
			elements.append(Spacer(0,0.1*inch))
			for [attendu,score] in liste_radar :
			    elements.append(Paragraph("Attendu : "+attendu+". Score : "+str(round(score))+"%",normal))
                            
	return elements
  
  
def print_monthly_statistiques(student,date_start,date_stop):

        buffer=BytesIO()
        doc = SimpleDocTemplate(buffer,
                                pagesize=A4, topMargin=0.3*inch,
				leftMargin=0.3*inch,
				rightMargin=0.3*inch,
				bottomMargin=0.3*inch	 )

        elements=pdfPeriode2(student, date_start,date_stop)

        doc.build(elements)
        
        pdf=buffer.getvalue()
        buffer.close()
        return pdf


def sendStats(parent,enfant,date_start,date_stop):
        doc=print_monthly_statistiques(enfant,date_start,date_stop)
        content = "Bonjour,\n\nvoici le rapport d'activité de " +  str(enfant.user.first_name)
        content+= "\npour la période du "+date_start.strftime("%d/%m/%y")+" au "+date_stop.strftime("%d/%m/%y")+"."
        content +="\n\nL'équipe Sacado."
        # developpement
        #email=EmailMessage("Rapport d'activité "+enfant.user.first_name,content,settings.DEFAULT_FROM_EMAIL,["stephan.ceroi@gmail.com"])
        #production
        email=EmailMessage("Rapport d'activité "+enfant.user.first_name,content,settings.DEFAULT_FROM_EMAIL,[parent.user.email])

        email.attach("Rapport_"+enfant.user.first_name+".pdf",doc, 'application/pdf')
        email.send()




  
