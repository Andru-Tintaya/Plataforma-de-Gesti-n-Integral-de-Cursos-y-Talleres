from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.cursos import cursos_bp
from app.extensions import db
from app.models import Curso, Inscripcion, Sesion, Asistencia

@cursos_bp.route('/mis-cursos')
@login_required
def mis_cursos():
    # DOCENTE: muestra sus cursos creados
    if current_user.rol.nombre == 'docente':
        mis_cursos = Curso.query.filter_by(docente_id=current_user.id).all()
        return render_template('cursos/mis_cursos.html', cursos=mis_cursos, es_docente=True)
    
    # ESTUDIANTE: muestra sus inscripciones pagadas
    mis_inscripciones = Inscripcion.query.filter_by(
        usuario_id=current_user.id,
        pago_verificado=True
    ).all()
    return render_template('cursos/mis_cursos.html', inscripciones=mis_inscripciones, es_docente=False)

@cursos_bp.route('/lista')
@login_required
def lista_cursos():
    gestion_actual = 2026
    cursos = Curso.query.filter_by(gestion=gestion_actual).all()
    return render_template('cursos/lista_cursos.html', cursos=cursos)

@cursos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_curso():
    if current_user.rol.nombre != 'docente':
        flash('No tienes permiso para crear cursos', 'warning')
        return redirect(url_for('cursos.mis_cursos'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo = request.form.get('codigo')
        paralelo = request.form.get('paralelo')
        num_sesiones = int(request.form.get('num_sesiones'))
        gestion = int(request.form.get('gestion'))
        
        nuevo_curso = Curso(
            nombre=nombre,
            codigo=codigo,
            paralelo=paralelo,
            num_sesiones=num_sesiones,
            docente_id=current_user.id,
            gestion=gestion
        )
        
        db.session.add(nuevo_curso)
        db.session.commit()
        
        flash('Curso creado exitosamente', 'success')
        return redirect(url_for('cursos.mis_cursos'))
    
    return render_template('cursos/crear_curso.html')

@cursos_bp.route('/inscribir/<int:curso_id>', methods=['POST'])
@login_required
def inscribir(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    
    existente = Inscripcion.query.filter_by(
        usuario_id=current_user.id,
        curso_id=curso_id
    ).first()
    
    if existente:
        flash('Ya estás inscrito en este curso', 'warning')
        return redirect(url_for('cursos.lista_cursos'))
    
    inscripcion = Inscripcion(
        usuario_id=current_user.id,
        curso_id=curso_id,
        pago_verificado=False
    )
    
    db.session.add(inscripcion)
    db.session.commit()
    
    flash('Inscripción exitosa. Espera la verificación del pago.', 'success')
    return redirect(url_for('cursos.mis_cursos'))

@cursos_bp.route('/detalle/<int:curso_id>')
@login_required
def detalle_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    
    # Verificar acceso
    es_docente = (curso.docente_id == current_user.id)
    inscripcion = None
    
    if not es_docente:
        inscripcion = Inscripcion.query.filter_by(
            usuario_id=current_user.id,
            curso_id=curso_id
        ).first()
        
        if not inscripcion or not inscripcion.pago_verificado:
            flash('No estás inscrito o tu pago no está verificado', 'warning')
            return redirect(url_for('cursos.mis_cursos'))
    
    sesiones = Sesion.query.filter_by(curso_id=curso_id).order_by(Sesion.numero).all()
    
    return render_template('cursos/detalle_curso.html', 
                         curso=curso, 
                         sesiones=sesiones,
                         inscripcion=inscripcion,
                         es_docente=es_docente)

@cursos_bp.route('/asistencia/<int:curso_id>', methods=['GET', 'POST'])
@login_required
def tomar_asistencia(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    
    # Solo el docente puede tomar asistencia
    if curso.docente_id != current_user.id:
        flash('Solo el docente puede tomar asistencia', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    if request.method == 'POST':
        sesion_numero = int(request.form.get('sesion_numero'))
        
        sesion = Sesion.query.filter_by(
            curso_id=curso_id,
            numero=sesion_numero
        ).first()
        
        if not sesion:
            sesion = Sesion(curso_id=curso_id, numero=sesion_numero)
            db.session.add(sesion)
            db.session.commit()
        
        inscripciones = Inscripcion.query.filter_by(
            curso_id=curso_id,
            pago_verificado=True
        ).all()
        
        for ins in inscripciones:
            clave = f'asistencia_{ins.id}'
            valor = request.form.get(clave)
            presente = True if valor == 'presente' else False
            
            asistencia = Asistencia.query.filter_by(
                inscripcion_id=ins.id,
                sesion_id=sesion.id
            ).first()
            
            if not asistencia:
                asistencia = Asistencia(
                    inscripcion_id=ins.id,
                    sesion_id=sesion.id,
                    presente=presente
                )
                db.session.add(asistencia)
            else:
                asistencia.presente = presente
        
        db.session.commit()
        flash('Asistencia registrada correctamente', 'success')
        return redirect(url_for('cursos.detalle_curso', curso_id=curso_id))
    
    # GET
    inscripciones = Inscripcion.query.filter_by(
        curso_id=curso_id,
        pago_verificado=True
    ).all()
    
    total_sesiones = list(range(1, curso.num_sesiones + 1))
    
    return render_template('cursos/tomar_asistencia.html',
                       curso=curso,
                       inscripciones=inscripciones,
                       sesiones=total_sesiones)