"""Arin | US-07 Sprint 4. Pure one-time location policy; no persistence/logging."""
import math

def distance_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2-p1, math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371008.8 * 2 * math.atan2(math.sqrt(max(0, a)), math.sqrt(max(0, 1-a)))

def check_sample(session, sample, now):
    if not session.opens_at <= now <= session.closes_at:
        return False, 'OUTSIDE_WINDOW'
    if sample['accuracy_m'] > session.max_accuracy_m:
        return False, 'LOW_ACCURACY'
    age = (now-sample['sampled_at']).total_seconds()
    if age < -5 or age > session.max_sample_age_seconds:
        return False, 'STALE_SAMPLE'
    if distance_m(sample['latitude'], sample['longitude'], session.centre_latitude, session.centre_longitude) > session.radius_m:
        return False, 'OUTSIDE_RADIUS'
    return True, 'WITHIN_POLICY'
