#!/usr/bin/env python
"""Test the episode formatting fix for missing season numbers"""
import django
import os

os.chdir(r'C:\Users\Nick\PycharmProjects\nstv')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.views import format_episode_info
from nstv.models import Show, Episode

print("\n" + "="*60)
print("TESTING EPISODE FORMAT FIX")
print("="*60)

# Test the helper function with various inputs
test_cases = [
    (1, 5, 'S1E5'),
    (None, 1, 'E1'),
    (None, None, ''),
    (1, None, 'S1'),
    (2, 3, 'S2E3'),
]

print("\n✓ Unit Tests:")
all_passed = True
for season, episode, expected in test_cases:
    result = format_episode_info(season, episode)
    passed = result == expected
    all_passed = all_passed and passed
    status = '✓' if passed else '✗'
    print(f'  {status} format_episode_info({season!r}, {episode!r}) = "{result}" (expected "{expected}")')

# Test with actual Feud episodes
print("\n✓ Integration Test (Feud show):")
feud = Show.objects.filter(title__icontains='Feud').first()
if feud:
    episodes = feud.episodes.all()[:3]
    for ep in episodes:
        formatted = format_episode_info(ep.season_number, ep.episode_number)
        print(f'  {feud.title} {formatted} - {ep.title}')
else:
    print("  ⚠ Feud show not found in database")

print("\n" + "="*60)
if all_passed:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")
print("="*60 + "\n")

