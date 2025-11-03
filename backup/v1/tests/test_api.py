#!/usr/bin/env python3
"""
Tests API avec simulation utilisateur complet.
"""

import json
import sys
from pathlib import Path

import requests

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

BASE_URL = "http://localhost:5000"


def test_api_endpoints():
    """Test tous les endpoints API."""
    print("=" * 80)
    print("TESTS API - Simulation Utilisateur")
    print("=" * 80)

    results = []

    # Test 1: Login
    print("\n1. Test Login...")
    try:
        login_data = {"username": "admin", "password": "admin"}
        response = requests.post(
            f"{BASE_URL}/api/auth/login", json=login_data, timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "token" in data:
                token = data["token"]
                print(f"✓ Login réussi, token obtenu: {token[:20]}...")
                results.append(True)
            else:
                print(f"✗ Login échoué: {data}")
                results.append(False)
        elif response.status_code == 404:
            print("⚠ Serveur non démarré ou endpoint non disponible")
            results.append(None)  # Skip
        else:
            print(f"✗ Erreur HTTP {response.status_code}: {response.text}")
            results.append(False)
    except requests.exceptions.ConnectionError:
        print("⚠ Serveur non démarré (Connection refused)")
        results.append(None)  # Skip
    except Exception as e:
        print(f"✗ Erreur: {e}")
        results.append(False)

    # Si login réussi, tester autres endpoints
    if results[0] is True:
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test 2: GET /api/auth/me
        print("\n2. Test GET /api/auth/me...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/auth/me", headers=headers, timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "user" in data:
                    print(f"✓ Récupération utilisateur: {data['user']['username']}")
                    results.append(True)
                else:
                    print(f"✗ Échec: {data}")
                    results.append(False)
            else:
                print(f"✗ Erreur HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur: {e}")
            results.append(False)

        # Test 3: GET /api/preferences
        print("\n3. Test GET /api/preferences...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/preferences", headers=headers, timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(
                        f"✓ Préférences récupérées: {len(data.get('preferences', []))} préférences"
                    )
                    results.append(True)
                else:
                    print(f"✗ Échec: {data}")
                    results.append(False)
            else:
                print(f"✗ Erreur HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur: {e}")
            results.append(False)

        # Test 4: POST /api/preferences
        print("\n4. Test POST /api/preferences...")
        try:
            pref_data = {
                "preference_key": "test_key",
                "preference_value": {"test": "value"},
            }
            response = requests.post(
                f"{BASE_URL}/api/preferences",
                json=pref_data,
                headers=headers,
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(
                        f"✓ Préférence créée: {data.get('preference', {}).get('preference_key')}"
                    )
                    results.append(True)
                else:
                    print(f"✗ Échec: {data}")
                    results.append(False)
            else:
                print(f"✗ Erreur HTTP {response.status_code}: {response.text}")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur: {e}")
            results.append(False)

        # Test 5: GET /api/jobs
        print("\n5. Test GET /api/jobs...")
        try:
            response = requests.get(f"{BASE_URL}/api/jobs", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✓ Jobs récupérés: {data.get('total', 0)} jobs")
                    results.append(True)
                else:
                    print(f"✗ Échec: {data}")
                    results.append(False)
            else:
                print(f"✗ Erreur HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur: {e}")
            results.append(False)

        # Test 6: GET /api/wizard/preferences
        print("\n6. Test GET /api/wizard/preferences...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/wizard/preferences?key=test",
                headers=headers,
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✓ Préférence wizard récupérée")
                    results.append(True)
                else:
                    print(f"✗ Échec: {data}")
                    results.append(False)
            else:
                print(f"✗ Erreur HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"✗ Erreur: {e}")
            results.append(False)

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ TESTS API")
    print("=" * 80)

    passed = sum(1 for r in results if r is True)
    skipped = sum(1 for r in results if r is None)
    failed = sum(1 for r in results if r is False)

    print(f"✓ Passés: {passed}")
    print(f"⚠ Skippés: {skipped}")
    print(f"✗ Échoués: {failed}")
    print(f"Total: {len(results)}")

    if skipped == len(results):
        print("\n⚠ Serveur non démarré - tests API non exécutés")
        return 2
    elif failed == 0:
        print("\n🎉 Tous les tests API sont passés!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(test_api_endpoints())
