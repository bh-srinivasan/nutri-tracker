#!/usr/bin/env python3
"""
Test if the app can start without errors
"""
try:
    print("🔄 Testing app creation...")
    from app import create_app
    
    print("✅ App import successful")
    
    app = create_app()
    print("✅ App creation successful")
    
    print(f"📋 Registered blueprints:")
    for blueprint in app.blueprints:
        print(f"   - {blueprint}")
    
    print(f"\n🔗 URL Map:")
    for rule in app.url_map.iter_rules():
        if '/api/' in rule.rule or '/docs/' in rule.rule:
            print(f"   {rule.methods} {rule.rule}")
    
    print("\n🎉 App configuration looks good!")
    
except Exception as e:
    print(f"❌ Error during app creation: {e}")
    import traceback
    traceback.print_exc()
