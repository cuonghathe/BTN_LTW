from flask import Blueprint, render_template, jsonify
from .models import db, Recipe, RecipeIngredient, Ingredient

recipe = Blueprint('recipe', __name__)

@recipe.route('/<int:recipe_id>', methods=['GET'])
def get_recipe_detail(recipe_id):
    # Truy vấn công thức
    recipe = db.session.query(Recipe).get(recipe_id)
    
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    # Truy vấn nguyên liệu liên quan
    ingredients = db.session.query(RecipeIngredient, Ingredient).\
        join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id).\
        filter(RecipeIngredient.recipe_id == recipe_id).all()

    # Chuẩn bị dữ liệu để render
    recipe_data = {
        'id': recipe.id,
        'name': recipe.name,
        'description': recipe.description,
        'instructions': recipe.instructions,
        'cooking_time': recipe.cooking_time,
        'serving_size': recipe.serving_size,
        'recipe_picture': recipe.recipe_picture,
        'date_added': recipe.date_added.strftime('%Y-%m-%d %H:%M:%S'),
        'ingredients': [
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'quantity': ri.quantity,
                'unit': ri.unit
            }
            for ri, ingredient in ingredients
        ]
    }

    # Render template
    return render_template('recipe_detail.html', recipe=recipe_data)

@recipe.route('/', methods=['GET'])
def get_recipes():
    # Truy vấn tất cả công thức
    recipes = Recipe.query.all()

    # Chuẩn bị dữ liệu để render
    recipes_data = [
        {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'recipe_picture': recipe.recipe_picture
        }
        for recipe in recipes
    ]

    # Render template danh sách công thức
    return render_template('recipe.html', recipes=recipes_data)