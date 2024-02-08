from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# load the model
def load_model(model_name):
    try:
        model = joblib.load(f'{model_name}_model.pkl')
        return model
    except FileNotFoundError:
        print(f"Model file not found. Please ensure '{model_name}_model.pkl' is in the correct path.")
        return None
    except Exception as e:
        print(f"Error loading the model: {str(e)}.")
        return None

@app.route('/predict', methods=['GET'])
def predict():
    try:
        # get the model input from the request
        model_name = request.args.get('model')
        model = load_model(model_name)
    except Exception as e:
        return jsonify({'error': f'Model loading failed: {str(e)}'})

    try:
        # get the features input from the request
        pclass = float(request.args.get('pclass'))
        age = float(request.args.get('age'))
        sibsp = float(request.args.get('sibsp'))
        parch = float(request.args.get('parch'))
        fare = float(request.args.get('fare'))
        alone = float(request.args.get('alone'))
        sex_male = float(request.args.get('sex_male'))
        embarked_Q = float(request.args.get('embarked_Q'))
        embarked_S = float(request.args.get('embarked_S'))
        class_Second = float(request.args.get('class_Second'))
        class_Third = float(request.args.get('class_Third'))
        embark_town_Queenstown = float(request.args.get('embark_town_Queenstown'))
        embark_town_Southampton = float(request.args.get('embark_town_Southampton'))

        # make prediction using the loaded model
        prediction = model.predict([[pclass,
                                     age,
                                     sibsp,
                                     parch,
                                     fare,
                                     alone,
                                     sex_male,
                                     embarked_Q,
                                     embarked_S,
                                     class_Second,
                                     class_Third,
                                     embark_town_Queenstown,
                                     embark_town_Southampton]])

        # return the prediction as JSON
        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)