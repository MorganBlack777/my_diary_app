from flask import Blueprint, render_template, redirect, url_for, abort, request, flash, make_response
from flask_login import login_required, current_user
from app.forms import EntryForm, SearchForm
from app.models import Entry, db, Tag
from sqlalchemy import or_
from io import BytesIO
import mistune
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.created_at.desc()).all()
    return render_template('index.html', entries=entries)

@main_bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    # Get all available tags for the dropdown
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.all()]
    
    if form.validate_on_submit():
        entry = Entry(title=form.title.data, content=form.content.data, author=current_user)
        # Add selected tags to the entry
        for tag_id in form.tags.data:
            tag = Tag.query.get(tag_id)
            if tag:
                entry.tags.append(tag)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('edit_entry.html', form=form)

@main_bp.route('/entry/<int:id>')
@login_required
def entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)  # Запрет доступа к чужим записям
    return render_template('entry.html', entry=entry)

@main_bp.route('/entry/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    form = EntryForm(obj=entry)
    # Get all available tags for the dropdown
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.all()]
    
    if form.validate_on_submit():
        # Update fields manually instead of using populate_obj
        entry.title = form.title.data
        entry.content = form.content.data
        
        # Clear existing tags and add selected ones
        entry.tags.clear()
        for tag_id in form.tags.data:
            tag = Tag.query.get(tag_id)
            if tag:
                entry.tags.append(tag)
        db.session.commit()
        return redirect(url_for('main.entry', id=entry.id))
    # Pre-select current tags
    form.tags.data = [tag.id for tag in entry.tags]
    return render_template('edit_entry.html', form=form, entry=entry)

@main_bp.route('/entry/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('main.index'))

@main_bp.route('/entry/<int:id>/export/pdf')
@login_required
def export_pdf(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    # Create a PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Convert markdown to plain text (simple approach)
    content = mistune.html(entry.content)
    
    # Create the PDF content
    elements = []
    elements.append(Paragraph(f'<b>{entry.title}</b>', styles['Title']))
    elements.append(Paragraph(f'Дата: {entry.created_at.strftime("%d.%m.%Y %H:%M")}', styles['Normal']))
    
    if entry.tags:
        tag_text = ', '.join([tag.name for tag in entry.tags])
        elements.append(Paragraph(f'Теги: {tag_text}', styles['Normal']))
    
    elements.append(Paragraph(content, styles['Normal']))
    
    # Build the PDF
    doc.build(elements)
    
    # Prepare response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=entry_{id}.pdf'
    
    return response

@main_bp.route('/entry/<int:id>/export/txt')
@login_required
def export_txt(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    # Create text content
    text_content = f"""
{entry.title}
Дата: {entry.created_at.strftime('%d.%m.%Y %H:%M')}
"""
    
    if entry.tags:
        text_content += f"Теги: {', '.join([tag.name for tag in entry.tags])}\n"
    
    text_content += f"\n{entry.content}"
    
    # Prepare response
    response = make_response(text_content)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename=entry_{id}.txt'
    
    return response

@main_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    results = []
    
    if request.method == 'POST' and form.validate_on_submit():
        query = form.query.data
        # Search in title, content and tags
        results = Entry.query.filter(
            Entry.user_id == current_user.id,
            or_(
                Entry.title.contains(query),
                Entry.content.contains(query),
                Entry.tags.any(Tag.name.contains(query))
            )
        ).all()
    
    return render_template('search.html', form=form, results=results)

@main_bp.route('/tag/<int:tag_id>')
@login_required
def tag_entries(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    entries = Entry.query.filter(
        Entry.user_id == current_user.id,
        Entry.tags.contains(tag)
    ).all()
    return render_template('index.html', entries=entries, tag=tag)

@main_bp.route('/tags', methods=['GET', 'POST'])
@login_required
def manage_tags():
    if request.method == 'POST':
        tag_name = request.form.get('tag_name', '').strip()
        if tag_name:
            # Check if tag already exists
            existing_tag = Tag.query.filter_by(name=tag_name).first()
            if existing_tag:
                flash('Тег с таким именем уже существует', 'warning')
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                flash('Тег успешно создан', 'success')
    
    # Get all tags
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)

@main_bp.route('/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Тег удален', 'success')
    return redirect(url_for('main.manage_tags'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')