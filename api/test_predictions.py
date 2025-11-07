"""
Test script for ML predictions API
Run this to verify the integration works
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_prediction_api():
    """Test the prediction endpoint"""
    print("="*70)
    print("Testing ML Predictions API")
    print("="*70)
    
    # Test data - minimal employee features
    test_request = {
        "employee_id": "test_employee_001",
        "features": {
            "age": 32,
            "experience_years": 5,
            "work_hours_per_day": 9.5,
            "overtime_hours": 15,
            "emails_sent": 45,
            "meetings_per_week": 12,
            "task_completion_rate": 0.75,
            "role_Developer": 1
        }
    }
    
    print("\n📤 Sending prediction request...")
    print(f"Employee ID: {test_request['employee_id']}")
    print(f"Features provided: {len([k for k, v in test_request['features'].items() if v is not None])}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predictions/predict",
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print("\n" + "="*70)
            print("PREDICTIONS")
            print("="*70)
            print(f"🔥 Burnout Risk: {result['burnout_percentage']:.1f}%")
            print(f"   Category: {result['risk_category']}")
            print(f"   {result['risk_description']}")
            print(f"\n💚 Wellbeing Score: {result['wellbeing_score']:.1f}/100")
            print(f"   Category: {result['wellbeing_category']}")
            print(f"\n⚡ Efficiency Score: {result['efficiency_score']:.1f}/100")
            print(f"   Category: {result['efficiency_category']}")
            print(f"\n📊 Data Completeness: {result['data_completeness']}")
            print(f"   Provided: {result['provided_features']} features")
            print(f"   Imputed: {result['imputed_features']} features")
            
            print("\n" + "="*70)
            print("RECOMMENDATIONS")
            print("="*70)
            for rec in result['recommendations']:
                print(f"  {rec}")
            print()
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the API server is running:")
        print("  cd api && python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_model_info():
    """Test the model info endpoint"""
    print("\n" + "="*70)
    print("Testing Model Info Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/predictions/model-info")
        
        if response.status_code == 200:
            info = response.json()
            print("\n✅ Model Information Retrieved")
            print(f"\nStatus: {info['status']}")
            print(f"Total Features: {info['total_features']}")
            
            print("\n" + "-"*70)
            print("Model Performance Metrics")
            print("-"*70)
            
            for model_name, metrics in info['models'].items():
                print(f"\n{model_name.replace('_', ' ').title()}:")
                print(f"  R² Score: {metrics['r2_score']:.4f}")
                print(f"  MAE: {metrics['mae']:.4f}")
                print(f"  RMSE: {metrics['rmse']:.4f}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_feature_importance():
    """Test feature importance endpoint"""
    print("\n" + "="*70)
    print("Testing Feature Importance")
    print("="*70)
    
    for model_type in ['burnout_risk', 'wellbeing', 'efficiency']:
        try:
            response = requests.get(
                f"{BASE_URL}/api/predictions/feature-importance/{model_type}?top_n=5"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n{model_type.replace('_', ' ').title()} - Top 5 Features:")
                print("-" * 50)
                for feature in data['top_features']:
                    print(f"  {feature['feature']:.<40} {feature['importance']:.4f}")
            else:
                print(f"❌ Error getting {model_type}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 ML Predictions API Test Suite\n")
    
    # Run tests
    test_prediction_api()
    test_model_info()
    test_feature_importance()
    
    print("\n" + "="*70)
    print("✨ Tests Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Integrate with frontend by calling /api/predictions/predict")
    print("2. Map Firebase employee data to feature format")
    print("3. Display burnout_percentage in the UI")
    print("4. Show recommendations to supervisors")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")
