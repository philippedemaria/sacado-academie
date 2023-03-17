import random
import re
import html
from django import template
register = template.Library()
from sendmail.models import Communication
import re



@register.filter
def add_parameters(arg, index):
    '''Modifie les paramètres aléatoires pour les questions flash'''
    tab = arg.split(";")
    if 'abscisse' in tab[0]:
        mini,maxi,step = tab[1].split(",")
        a = random.randint(int(mini),int(maxi))*int(step)
        b = a+int(tab[2])
        arg = arg.replace("x",str(a))
        string = arg.replace("y",str(b))
        new_str = string[:-1]+","+str(index)+")"
        new_str = new_str.split(";")[0]
        new_str = new_str[:-1]+","+str(index)+")"

    elif 'pizza' in tab[0] or 'chocolat' in tab[0] :
        mini,maxi = tab[1].split(",")
        a = random.randint(int(mini),int(maxi))
        arg = arg.replace("n",str(a))
        if len(tab)>1:
            minim,maxim = tab[2].split(",")
            b = random.randint(int(minim),int(maxim))
            string = arg.replace("d",str(b))
        new_str = string[:-1]+","+str(index)+")"
        new_str = new_str.split(";")[0]
        new_str = new_str[:-1]+","+str(index)+")"
    else :
        new_str = arg[:-1]+","+str(index)+")"
    return new_str



@register.filter
def is_checked(arg):
    '''input est-il checked ?'''
    return 'checked' in str(arg)



@register.filter
def no_iframe(arg):
    '''HTML entity decode'''
    arg = arg.replace('<iframe','___#iframe#___')
    arg = arg.replace('</iframe>','___#iframe#___')
    tab_arg = arg.split('___#iframe#___')
    string = ""
    for i in range(0,len(tab_arg),2) :
        string += tab_arg[i]
    return string.strip()

@register.filter
def close_div(arg):
    '''HTML entity decode'''
    nb_div = arg.count('<div')
    nb_cdiv = arg.count('</div>')
    if nb_div > nb_cdiv :
        loop = nb_div - nb_cdiv
        for i in range(loop):
            arg += "</div>"
    return arg

@register.filter
def no_image(arg):
    '''HTML entity decode'''
    arg = arg.replace('<img','___#image#___')
    arg = arg.replace('/>','___#image#___')
    tab_arg = arg.split('___#image#___')
    string = ""
    for i in range(0,len(tab_arg),2) :
        string += tab_arg[i]
    return string.strip()


@register.filter
def no_table(arg):
    '''HTML entity decode'''
    arg = arg.replace('<table','___#table#___')
    arg = arg.replace('</table>','___#table#___')
    tab_arg = arg.split('___#table#___')
    string = ""
    for i in range(0,len(tab_arg),2) :
        string += tab_arg[i]
    return string.strip()



@register.filter
def splitter(arg):
    '''HTML entity decode'''
    new= []
    for a in arg.split('##') :
        try :
            new.append(int(a))
        except :
            pass
    return new


@register.filter
def filltheblanks_safe(arg):
    '''HTML entity filltheblanks_safe'''
    arg = arg.replace('<strong>','####')
    arg = arg.replace('</strong>','####')
    tab = arg.split('####')

    string = ""
    for i in range(len(tab)) :
        
        if i%2==1:
            if  int(len(tab[i]))  < 4 : ln = "30"
            elif  int(len(tab[i]))  < 10 : ln = "100"
            else : ln = str(int(len(tab[i]))*10)
            st = " <input type='text' style='border:1px solid #CCC; width:"+ln+"px;border-radius:4px;text-align:center' value='"+tab[i]+"'   />"
        else :
            st = tab[i] 
        string += st
    return string




@register.filter
def insert_input(arg,loop):
    '''HTML entity filltheblanks_safe'''
    arg = arg.replace('<strong>','####')
    arg = arg.replace('</strong>','####')
    tab = arg.split('####')

    string = ""
    j=1

    for i in range(len(tab)) :
        if i%2==1:
            st = "<input type='hidden' name='answers"+str(loop)+"' id='loop_"+str(loop)+"-"+str(j)+"' /><div class='input_droppable droppable"+str(loop)+"' data-subloop='"+str(j)+"'></div>"
            j+=1
        else :
            st = tab[i] 
        string += st
    return string



@register.filter
def insert_only_input(arg,loop):
    '''HTML entity filltheblanks_safe'''
    arg = arg.replace('<strong>','####')
    arg = arg.replace('</strong>','####')
    tab = arg.split('####')

    string = ""
    for i in range(len(tab)) :
        if i%2==1:
            if  int(len(tab[i]))  < 4 : ln = "60"
            elif  int(len(tab[i]))  < 10 : ln = "200"
            else : ln = str(int(len(tab[i]))*10)
            st = "<input type='text' name='answers"+str(loop)+"' style='width:"+str(ln)+"px;'  class='answer_the_blanks answer_fill_the_blanks'  />"
        else :
            st = tab[i] 
        string += st
    return string






@register.filter
def question_input(arg):
    '''HTML entity filltheblanks_safe'''
    arg = arg.replace('<strong>','####')
    arg = arg.replace('</strong>','####')
    tab = arg.split('####')

    string = ""
    j=1

    for i in range(len(tab)) :
        if i%2==1:
            st = "<input type='hidden' name='solution' id='loop_"+str(loop)+"-"+str(j)+"' /><div class='input_droppable droppable"+str(loop)+"' data-subloop='"+str(j)+"'></div>"
            j+=1
        else :
            st = tab[i] 
        string += st
    return string



@register.filter
def question_only_input(arg):
    '''HTML entity filltheblanks_safe'''
    arg = arg.replace('<strong>','####')
    arg = arg.replace('</strong>','####')
    tab = arg.split('####')

    string = ""
    for i in range(len(tab)) :
        if i%2==1:
            if  int(len(tab[i]))  < 4 : ln = "60"
            elif  int(len(tab[i]))  < 10 : ln = "200"
            else : ln = str(int(len(tab[i]))*10)
            st = "<input type='text' name='solution' style='width:"+str(ln)+"px;'  class='answer_the_blanks answer_fill_the_blanks'  />"
        else :
            st = tab[i] 
        string += st
    return string



@register.filter
def these_accepted_solutions(arg):
    '''HTML entity filltheblanks_safe'''
    return arg.replace('____',' ; ')
 

@register.filter
def shuffle(arg):
    my_list = list(arg)
    random.shuffle(my_list)
    return my_list    
 
 

@register.filter
def decode(arg):
    '''HTML entity decode'''
    string = html.unescape(arg)
    return string
 

@register.filter
def keep_point(arg):
    '''garde le point au lieu de la virgule'''
    return str(arg).replace(",",".")


@register.filter
def decrypt_results(arg):
    '''Pour les flashcards'''
    tab = arg.split("-")
    string = ""
    for r in tab :
        if r == '' :
            score = None
        elif int(r) == 1 :
            score = "danger"
        elif int(r) == 3 :
            score = "validate"
        elif int(r) == 5 :
            score = "success"
        if score  :
            string += "<i class='fa fa-square fa-xs text-"+score+"'></i>"
        
    return string





@register.filter
def cleanhtml(raw_html): #nettoie le code des balises HTML
    cleantext = re.sub('<.*?>', '', raw_html)
    cleantext = re.sub('\n', '', cleantext)
    return cleantext


 

@register.filter
def decimal2number(decimal): #enlève la virgule et met un point
    d_tab = str(decimal).replace(",",".") 
    return d_tab



@register.filter
def abreviation(raw_html): #nettoie le code des balises HTML
    if raw_html.isdigit():
        if raw_html == "Term" :
            return str("T<sup>erm</sup>")
        elif raw_html == "1" :
            return str("1<sup>ère</sup>")
        elif raw_html == 2 :
            return str("2<sup>nde</sup>")
        else :
            return str(raw_html) + "<sup>ème</sup>" 
    else :
        return raw_html


@register.filter
def marker_details(string): #marker_coordonnees pour les exercices de placement sur image
    data = {}
    try :
        classe,abscisse,ordonnee = string.split("|")
        data['coordonnees'] = "left:{}px;top:{}px".format(abscisse, ordonnee)
        data['classe'] = classe
    except :
        pass
    return data


@register.filter
def marker_details_answer(string): #marker_coordonnees pour les exercices de placement sur image
    data = {}
    try :
        classe,abscisse,ordonnee = string.split("|")
        ordonnee = int(ordonnee)-25 
        data['coordonnees'] = "left:{}px;top:{}px".format(abscisse, ordonnee)
        data['classe'] = classe
    except :
        pass
    return data


@register.filter
def counting(obj): #compte le nombre d'exercice sans titre
    return obj.filter(supportfile__is_title=0).count()




@register.filter
def not_title(obj): #renvoie les supportfile qui ne sont pas des titles
    return obj.filter(is_title=0) 




@register.filter
def exclude_teacher(obj): #exclusion des enseignants de la liste renvoyées
    return obj.exclude(user__username__contains="_e-test").order_by("user__last_name")




@register.filter
def insert_tags(html,cutter): #nettoie le code des balises HTML
    i = 1
    if "iframe" in html :
        return html
    else:
        htm = html[:cutter]
        while i*cutter < len(html) : 
                htm += html[i*cutter:(i+1)*cutter].replace(" ","<br>",1)
                i += 1
        return "<p>"+htm+"</p>"


@register.filter
def top_less(html,up): #Réduit le top

    htm_css_tab = html.split(";")#récupère chaque propriétés du css

    htm_propriete_tab = []
    for css in htm_css_tab : 
        propriete =  css.split(":") 
        htm_propriete_tab.append(propriete)

    for prop in htm_propriete_tab :
        if "top" in prop[0] : 
            prop[1] = str(int(prop[1][:-2])-up)+"px"
            break
 
    chaine = ""
    for i in range(len(htm_propriete_tab)-1):
        chaine += str(htm_propriete_tab[i][0])+":"+str(htm_propriete_tab[i][1])+";"
    return chaine

@register.filter
def index(sequence, position):
    """
    Renvoie la valeur dans une sequence donné sur un index donné
    """
    return sequence[position]


@register.simple_tag 
def get_score(obj,student): 
    """
    retourne le  score d'un même exercice par élève.
    """
    return obj.send_score(student) 

 
@register.simple_tag 
def get_min_score(obj,student): 
    """
    retourne le  score d'un même exercice par élève.
    """
    return obj.min_score(student) 


 

@register.simple_tag
def get_score2(results, id):
    """
    regarde si l'id est dans le dictionnaire results et renvoie le score associé ( ou '' dans le cas contraire)
    """
    return results.get(id, '')



@register.simple_tag
def get_is_lock(obj,todaytimer): 
    """Bloque un exercice dans une évaluation si celui-ci a une date de verrou"""
    return obj.is_lock(todaytimer)



@register.simple_tag
def get_available(obj,student): 
    """ Détermine si un exercice est enregistrable pour un élève lors d'une évaluation au vue du nombre de tentatives"""
    return obj.is_available(student)

@register.simple_tag
def get_parcours_available(obj,student,exercise): 
    """ Détermine si un exercice est enregistrable pour un élève lors d'une évaluation au vue du nombre de tentatives"""
    return obj.is_available(student,exercise)


@register.simple_tag
def get_is_locker(obj,student): 
    """Permet de déverrouiller un exercice dans une évaluation pour qeulques élèves """
    return obj.is_locker(student)




@register.simple_tag
def get_is_lock_for_this_parcours(obj, parcours , today) :
    return obj.is_lock_this_parcours(parcours , today)



@register.simple_tag
def get_is_submitted(obj,student): 
    """Vérifie si un exercice non auto corrigé est envoyé par un élève"""
    return obj.is_submit(student)



@register.simple_tag
def get_is_submit(obj,parcours,student): 
    """Vérifie si un exercice non auto corrigé est envoyé par un élève"""
    return obj.is_submit(parcours,student)


@register.simple_tag 
def get_scores(obj,student):
    """
    retourne les scores d'un même exercice par élève.
    """ 
    return obj.send_scores(student)

@register.simple_tag
def get_timer(obj,student): 
    """
    retourne  l'heure d'un exerice fait par élève.
    """
    return obj.timer(student) 



@register.simple_tag
def get_ans_for_this_question(obj,q, student): 
    """
    retourne  la réponse pour un quizz avec une question. peutn être sous forme d'id.
    """
    return obj.ans_for_this_question(q, student) 



@register.simple_tag
def get_real_ans_for_this_question(obj,q, student): 
    """
    retourne  la réponse pour un quizz avec une question sous forme du choix proposé.
    """
    return obj.real_ans_for_this_question(q, student) 





@register.simple_tag ##
def get_score_and_time(obj,student):
    """
    retourne la liste des scores et l'heure d'un exercice fait par élève.
    """
    return obj.score_and_time(student) 


@register.simple_tag  
def get_last_score_and_time(obj,parcours,student): 
    """
    retourne le dernier score et l'heure d'un exercice fait par élève.
    """
    return obj.last_score_and_time(parcours,student) 


@register.simple_tag  
def get_percent_done(obj,parcours): 
    """
    retourne le pourcentage d'exercice fait dans un parcours par élève.
    """
    return obj.percent_done(parcours) 


@register.simple_tag  
def get_is_selected(obj,parcours): # Utiliser aussi pour bibliotex avec parcours = bibliotex_id
    """
    retourne si un exercice est choisi dans un parcours.
    """
    return obj.is_selected(parcours) 


@register.simple_tag  
def get_ranking(obj,parcours): 
    """
    retourne le rang d'un exercice est choisi dans un parcours.
    """
    return obj.is_ranking(parcours) 

@register.simple_tag 
def get_percent(obj,student): 
    """
    retourne le pourcentage d'exercices fait sur un parcours.
    """
    return obj.is_percent(student) 


@register.simple_tag  
def get_done(obj,student):
    """
    teste si l'exercice est fait.
    """ 
    return obj.is_done(student) 


@register.simple_tag 
def get_affect(obj,student): 
    """
    teste le nombre d'exercices faits sur un parcours.
    """
    return obj.is_affect(student) 
 

@register.simple_tag ##  
def get_resultexercises_by_theme(obj,theme): 
    """
    Renvoie les exercices selon thème d'un élève 
    """
    return obj.resultexercises_by_theme(theme) 


@register.simple_tag   
def get_resultknowledge_by_theme(obj,theme): 
    """
    Renvoie les exercices selon thème d'un élève
    """
    return obj.resultknowledge_by_theme(theme) 



@register.simple_tag   
def get_level_theme(obj,theme): 
    """
    Renvoie les exercices selon thème d'un élève
    """
    return obj.is_level_theme(theme) 







@register.filter
def contrast_color(color):
    """
    Renvoie la couleur N/B en contraste
    """
    try :
        color_test = 0.299 * int(color[1:3],16) + 0.587 * int(color[3:5],16) + 0.114 * int(color[5:7],16)
    except :
        try :
            if 'rgba' in color :
                color_tab = color[5:].split(",")
                color_test = 0.299 * int(color[0]) + 0.587 * int(color[1]) + 0.114 * int(color[2])
            else :
                color_test = 10
        except :
            color_test = 10
    if color_test > 200 :
        return "#20123a"
    else :
        return "#FFFFFF"


@register.filter
def contrast_color_title(color):
    """
    Renvoie la couleur N/B en contraste
    """
    try :
        color_test = 0.299 * int(color[1:3],16) + 0.587 * int(color[3:5],16) + 0.114 * int(color[5:7],16)
    except :
        try :
            if 'rgba' in color :
                color_tab = color[5:].split(",")
                color_test = 0.299 * int(color[0]) + 0.587 * int(color[1]) + 0.114 * int(color[2])
            else :
                color_test = 10
        except :
            color_test = 10
    if color_test > 200 :
        return "#20123a"
    else :
        return color



@register.filter
def cleanhtml(arg):
    """
    nettoie le code html
    """
    try :
        cleantext = re.sub('<.*?>', '', arg)
        cleantext = re.sub('\n', '', cleantext)
        cleantext = html.unescape(cleantext)
    except : 
        cleantext = arg
    return cleantext


@register.filter
def time_done(arg):
    """
    convertit 1 entier donné  (en secondes) en durée h:m:s
    """
    def pad(number):
        """" ajoute un zéro devant un entier inférieur à 10 """
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)

    if arg == "":
        return arg
    else:
        arg = int(arg)
        s = pad(arg % 60)
        m = pad(arg // 60 % 60)
        h = pad(arg // 3600)
        
        if arg < 60:
            return f"{s}s"
        if arg < 3600:
            return f"{m}min.{s}s"
        else:
            return f"{h}h.{m}min.{s}s"



@register.filter
def int_minutes(arg):  
    """
    convertit 1 entier donné (en minutes) en durée
    """
    if arg == "" :
        r = ""
    else :
        arg = int(arg)
        if arg < 60 :
            h = "00"
            m = arg
            r = str(m)
        else :
            h = int(arg/60)
            m = arg%60
            if m<10 :
                minutes = "0"+str(m)
            else :
                minutes = str(m)
            r = str(h)+"h."+minutes        
    return r



@register.filter
def int_to_min(arg):
    """
    convertit 1 entier en minutes
    """

    if arg == "":
        return arg
    elif arg < 60:
        return arg
    else :
        m = arg // 60
        return int(round(m,1))








@register.simple_tag ##  
def get_relationship(obj,parcours): 
    return obj.is_relationship(parcours) 
 
@register.simple_tag  
def get_used_in_parcours(obj,teacher): 
    return obj.used_in_parcours(teacher) 

@register.simple_tag  
def get_parcourses_from_level(obj,teacher): 
    return obj.parcourses_from_level(teacher) 

@register.simple_tag  
def get_folders_from_level(obj,teacher): 
    return obj.folders_from_level(teacher) 

@register.simple_tag  
def get_question_is_already_used(obj,teacher): 
    return obj.is_already_used(teacher) 
 
@register.simple_tag  
def get_scorek(obj,student): 
    """
    résultats d'un savoir faire par élève
    """
    return obj.send_scorek(student)

 
@register.simple_tag  
def get_scorekp(obj,student,parcours): 
    """
    résultats d'un savoir faire par élève
    """
    return obj.send_scorekp(student,parcours)

@register.simple_tag  
def get_exercises_by_knowledge(obj,student,group):
    return obj.exercices_by_knowledge(student,group)


@register.simple_tag  
def get_only_students(obj,group):
    return obj.only_students(group)




@register.simple_tag  
def get_used_in_group(obj,group): 
    """
    Si un objet est utilisé dans un groupe
    """
    return obj.used_in_group(group) 

 


@register.simple_tag  
def get_my_relationships(obj,parcourses): 
    """
    Récupère les relationships utilisées dans un groupe à partir d'un obj  (waiting et knowledge) 
    """
    return obj.my_relationships(parcourses) 



@register.simple_tag 
def get_exercise_used(obj,parcours_tab): 
    """
    teste si un exerice est utilisé dans un groupe
    """
    return obj.nb_exercise_used(parcours_tab)


@register.simple_tag  
def get_score_by_theme(obj,student,group): 
    """
    retourne le score par thème d'un groupe par élève
    """
    return obj.as_score_by_theme(student,group)


@register.simple_tag
def get_knowledge_average(obj,group): 
    """
    retourne le score moyen des exercices par élève d'un groupe
    """
    return obj.knowledge_average(group)


@register.simple_tag
def get_knowledge_worked(obj,student): 
    return obj.nb_knowledge_worked(student)

@register.simple_tag
def get_nb_leaf(obj,student): 
    """
    envoie le nombre de sous parcours
    """
    return obj.nb_leaf(student)



@register.simple_tag
def get_nb_task_done(obj,group): 
    """
    retourne le nombre de taches données par groupe
    """
    return obj.nb_task_done(group)


@register.simple_tag
def get_who_are_done(obj,group): 
    """
    retourne une liste des élèves du groupes qui ont fait l'exercice.
    """
    return obj.who_are_done(group)


@register.simple_tag ##  retourne le nombre de taches données par parcours
def get_nb_task_parcours_done(obj,parcours): 
    return obj.nb_task_parcours_done(parcours)


@register.simple_tag
def get_who_are_done_parcours(obj,parcours): 
    """
    retourne une liste des élèves du parcours qui ont fait l'exercice.
    """
    return obj.who_are_done_parcours(parcours)



@register.simple_tag 
def get_exercise(obj, exercise): 
    """
    booleen si l'élève appartient ou pas à un parcours
    """
    return obj.has_exercise( exercise)



@register.simple_tag 
def get_customexercise(obj, exercise): 
    """
    booleen si l'élève appartient ou pas à un parcours
    """
    return obj.has_customexercise( exercise)





@register.simple_tag 
def get_all_details(obj,parcours): 
    """
    retourne le nombre d'exercices par parcours publiés.
    """
    return obj.all_details(parcours)




@register.simple_tag 
def get_is_leaf(obj,parcours): 
    """
    retourne le nombre d'exercices par parcours publiés.
    """
    return obj.p_is_leaf(parcours)



@register.simple_tag  
def get_in_parcours(obj, parcours):
    """
    booleen si l'élève appartient ou pas à un parcours
    """ 
    return obj.is_in_parcours( parcours)


 
@register.simple_tag 
def get_score_student_parcours(obj,student, parcours): 
    return obj.score_student_parcours(student, parcours)

 
@register.simple_tag 
def get_score_student_parcours(obj,student, parcours): 
    return obj.score_student_parcours(student, parcours)

@register.simple_tag  
def get_this_exercise_is_locked(obj,exercise, parcours , custom, today): 
    """
    L'exercice ou la relation est bloqué pour l'objet student
    """
    return obj.this_exercise_is_locked(exercise, parcours, custom, today)



@register.simple_tag  
def get_percent_student_done_parcours_exercice_group(obj,parcours, group): 

    return obj.percent_student_done_parcours_exercice_group(parcours,group)



@register.simple_tag 
def get_score_student_for_this(obj, student): 
    """
    renvoie le score par relation pour un étudiant donné
    """
    return obj.score_student_for_this(student)



@register.simple_tag 
def get_code_student_for_this(obj, student): 
    """
    renvoie le score par relation pour un étudiant donné
    """
    return obj.code_student_for_this(student)



@register.simple_tag
def get_constraint_to_this_relationship(obj, student): 
    """
    teste si la relationship est sous constrainte pour cet élève
    """
    return obj.constraint_to_this_relationship(student)






@register.simple_tag 
def get_documents_counter_by_student(obj, group): 
    """
    Compte
    """
    return obj.documents_counter_by_student(group)




@register.simple_tag 
def get_an_association_knowledge_supportfile(obj, supportfile): 
    """
    renvoie le score par relation
    """
    return obj.association_knowledge_supportfile(supportfile)

@register.simple_tag 
def get_parcours_group_students_count(obj, group):
    """
    renvoie le nombre de parcours
    """ 
    return obj.parcours_group_students_count(group)


@register.simple_tag ## 
def get_details(obj,  parcours): 
    return obj.details(parcours)



@register.simple_tag 
def get_tasks(obj,  parcours): 
    """
    renvoie le score par knowledge 
    """
    return obj.is_task_exists(parcours)



@register.simple_tag  
def get_result_skills(obj,  skill): 
    """
    renvoie le score par knowledge 
    """
    return obj.result_skills(skill)



@register.simple_tag  
def get_bilan_skills(obj,  skill): 
    """
    renvoie le score par knowledge 
    """
    return obj.bilan_skills(skill)




 
@register.simple_tag  
def get_skill_result(obj,  skill ,student): 
    """
    renvoie le score par skill et par relationship par élève 
    """
    return obj.result_skill( skill ,student)




@register.simple_tag  
def get_result_waitings(obj,  waiting): 
    """
    renvoie le score par waiting 
    """
    return obj.result_waitings(waiting)





@register.simple_tag 
def get_access_to_this_group(obj,  teacher):
    """
    Donne l'accès à un groupe à un enseignant
    """
    return obj.authorize_access(teacher)


@register.simple_tag 
def get_group_parcours_counter(obj,  teacher):
    """
    Contre le nombre de parcours associé à un groupe d'un enseignant donné
    """
    return obj.parcours_counter(teacher)


@register.simple_tag 
def get_parcours_from_this_exercise(obj,  teacher):
    """
    renvoie les parcours d'un enseignant donné liés à un exercice
    """
    return obj.my_parcours_container(teacher)


@register.simple_tag 
def get_com_is_reading(user):
    """
    renvoie les parcours d'un enseignant donné liés à un exercice
    """
    return Communication.com_is_reading(user)

@register.simple_tag 
def get_sharing_role(obj,  teacher):
    """
    renvoie les parcours d'un enseignant donné liés à un exercice
    """
    return obj.sharing_role(teacher)


@register.simple_tag 
def get_corrected_for_this(obj, student, parcours):
    """
    renvoie les parcours d'un enseignant donné liés à un exercice
    """
    return obj.is_corrected_for_this(student, parcours)



@register.simple_tag 
def get_result_k_s(obj, k_s, student, parcours,typ):
    """
    renvoie les résultats d'une skill ou d'une knowledge d'un exercice
    """
    return obj.result_k_s(k_s, student, parcours,typ)


@register.simple_tag
def get_percent_to_parcours(obj,student): 
    """
    retourne  le pourcentage des réponses pour un quizz et des exercices GGB d'un parcours.
    """
    return obj.is_percent_to_parcours(student) 


@register.simple_tag 
def get_mark_to_this(obj, student, parcours):
    """
    renvoie la note d'un exercice custom
    """
    return obj.mark_to_this(student, parcours)


@register.simple_tag 
def get_all_results_custom(obj, student, parcours):
    """
    renvoie le résultat d'un exo custom coté élève
    """
    return obj.all_results_custom(student, parcours)


@register.simple_tag 
def get_custom_score(obj, customexercise, student, parcours):
    """
    renvoie le résultat d'un exo custom coté élève
    """
    return obj.custom_score(customexercise, student, parcours)


@register.simple_tag 
def get_result_skills_custom(obj, skill):
    """
    renvoie le résultat des compétences corrigé par l'enseignant pour l'enseignant
    """
    return obj.result_skills_custom(skill)


@register.simple_tag 
def get_noggb_data(obj, student):
    """
    renvoie le résultat d'un exo custom coté élève
    """
    return obj.noggb_data(student)


@register.simple_tag 
def get_vote(obj, user):
    """
    renvoie le résultat d'un exo custom coté élève
    """
    return obj.has_vote(user)



@register.simple_tag 
def get_group_in_this_school(obj, school):
    """
    obj = teacher , renvoie les groupes de cet enseignant dans l'école
    """
    return obj.group_in_this_school(school)


@register.simple_tag 
def get_quizz_generated(obj, group):
    """
    obj = quizz ,  historique des quizz
    """
    return obj.quizz_generated(group)  


@register.simple_tag 
def get_is_correct_answer_quizz_random(obj, student):
    """
    obj = qr ,  prédicat : question juste ou fausse par élève
    """
    return obj.is_correct_answer_quizz_random(student)  


@register.simple_tag 
def get_is_correct_answer_quizz(obj, student):
    """
    obj = qr ,  prédicat : question juste ou fausse par élève
    """
    return obj.is_correct_answer_quizz_random(student)  


@register.simple_tag 
def get_score_quizz_random(obj, g_quizz):
    """
    obj = student ,  renvoie par élève le score total au quizz et le niveau de knowledge
    """
    return obj.score_quizz_random(g_quizz)  

 

@register.simple_tag 
def get_historic_aefe(obj, parcours):
    """
    obj = teacher ,  renvoie si l'enseignant a récupéré les parcours aefe
    """
    return obj.historic_aefe(parcours)  



@register.simple_tag 
def get_nb_level_subject(obj, subject_id):
    """
    Donne le nombre d'exercices sur un niveau dans une matière donnée
    """
    return obj.nb_level_subject(subject_id)  


@register.simple_tag 
def is_can_quizz_restart(obj, student):
    """
    Détermine si un élève a déjà fini son quizz depuis la page tool/list_quizz_student.html
    """
    return obj.restart_quizz(student)



@register.simple_tag 
def get_success_percent(obj, quizz):
    """
    Détermine le pourcentage de bonne réponse à une question du gquizz
    """
    return obj.success_percent(quizz)



@register.simple_tag 
def get_students_from_group_and_folder(obj, group):
    """
    Détermine le pourcentage de bonne réponse à une question du gquizz
    """
    return obj.group_and_folder_only_students(group)




@register.simple_tag 
def get_students_from_group_and_rc(obj, group):
    """
    Détermine le pourcentage de bonne réponse à une question du gquizz
    """
    return obj.group_and_rc_only_students(group)





@register.simple_tag 
def get_data_parcours_evaluations_from_group_folder(obj, group):
    """
    Détermine le pourcentage de bonne réponse à une question du gquizz
    """
    return obj.data_parcours_evaluations_from_group(group)


@register.simple_tag 
def get_publish_parcours_inside_folder (obj,folders,student):
    """Détermine si un parcours est publié et s'il est dans un dossier publié """
    return obj.publish_parcours_inside_folder(folders,student)  


 

@register.simple_tag 
def get_today_cards (obj,today,student):
    """Détermine si un parcours est publié et s'il est dans un dossier publié """
    return obj.today_cards(today,student)  


 

@register.simple_tag 
def get_result_by_student (obj,flashpack,student):
    """Détermine si une flashcard a été répondu par un student et pour un flashpack donné """
    return obj.is_result_by_student(flashpack,student)  


 

@register.simple_tag 
def get_flashpack_by_student (obj, student):
    """Détermine si un flashpack  est traité par un élève """
    return obj.is_result_by_student( student)  


@register.simple_tag 
def get_criterion_results (obj, customexercise, parcours , student):
    """Détermine si un flashpack  est traité par un élève """
    return obj.results( customexercise, parcours , student) 
 

@register.simple_tag 
def include_in_flashpack (obj, flashpack):
    """Détermine si un flashpack  est traité par un élève """
    return obj.in_flashpack( flashpack ) 
 



@register.simple_tag 
def get_permit_access (obj, model):
    """ Vérifie l'accès pour un modèle cloné """
    return obj.permit_access( model ) 


@register.simple_tag
def is_inside_my_lesson(obj,student): 
    """
    retourne  la réponse pour un quizz avec une question. peutn être sous forme d'id.
    """
    return obj.student_in_my_lesson(student) 

