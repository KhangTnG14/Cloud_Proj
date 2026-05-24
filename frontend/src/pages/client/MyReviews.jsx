// frontend/src/pages/client/MyReviews.jsx

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

import binIcon from '../../assets/delete.png';
import editIcon from '../../assets/edit.png';
import worldTourIcon from '../../assets/world-tour.png';


const token = () => localStorage.getItem('access_token');

function StarDisplay({ rating }) {
  return (
    <span style={{ color: '#f59e0b', fontSize: '18px', letterSpacing: '2px' }}>
      {'★'.repeat(rating)}
      <span style={{ color: '#d1d5db' }}>{'★'.repeat(5 - rating)}</span>
    </span>
  );
}

function StarInput({ value, onChange }) {
  const [hovered, setHovered] = useState(0);
  return (
    <div style={{ display: 'flex', gap: '4px', margin: '8px 0' }}>
      {[1,2,3,4,5].map(star => (
        <span
          key={star}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(0)}
          style={{
            fontSize: '28px', cursor: 'pointer',
            color: star <= (hovered || value) ? '#f59e0b' : '#d1d5db',
            transition: 'color 0.15s',
          }}
        >★</span>
      ))}
    </div>
  );
}

function ThreeDotMenu({ onEdit, onDelete }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef();

  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target))
        setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={menuRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          background: open ? '#f3f4f6' : 'none',
          border: 'none', cursor: 'pointer',
          fontSize: '22px', color: '#9ca3af',
          padding: '4px 10px', borderRadius: '6px',
          lineHeight: 1, transition: 'background 0.2s',
        }}
        onMouseEnter={e => e.currentTarget.style.background = '#f3f4f6'}
        onMouseLeave={e => e.currentTarget.style.background = open ? '#f3f4f6' : 'none'}
      >⋮</button>

      {open && (
        <div style={{
          position: 'absolute', right: 0, top: '110%',
          background: 'white', border: '1px solid #e5e7eb',
          borderRadius: '10px', boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          minWidth: '150px', zIndex: 100, overflow: 'hidden',
        }}>
          <button
            onClick={() => { onEdit(); setOpen(false); }}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              width: '100%', padding: '11px 16px',
              background: 'none', border: 'none',
              cursor: 'pointer', fontSize: '14px', color: '#374151', textAlign: 'left',
            }}
            
            onMouseEnter={e => e.currentTarget.style.background = '#f9fafb'}
            onMouseLeave={e => e.currentTarget.style.background = 'none'}
          >
            <img
              src={editIcon}
              alt="Edit"
              style={{
                width: '16px',
                height: '16px',
                objectFit: 'contain',
                  }}
            />
            Sửa đánh giá</button>

          <div style={{ height: '1px', background: '#f3f4f6' }} />

          <button
            onClick={() => { onDelete(); setOpen(false); }}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              width: '100%', padding: '11px 16px',
              background: 'none', border: 'none',
              cursor: 'pointer', fontSize: '14px', color: '#ef4444', textAlign: 'left',
            }}
            onMouseEnter={e => e.currentTarget.style.background = '#fef2f2'}
            onMouseLeave={e => e.currentTarget.style.background = 'none'}
          ><img
            src={binIcon}
            alt="Delete"
            style={{
              width: '16px',
              height: '16px',
              objectFit: 'contain',
            }}
          /> Xóa đánh giá</button>
        </div>
      )}
    </div>
  );
}

function ReviewCard({ review, onDeleted, onUpdated }) {
  const [editing, setEditing]   = useState(false);
  const [content, setContent]   = useState(review.content);
  const [rating, setRating]     = useState(review.rating);
  const [saving, setSaving]     = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm(`Xóa đánh giá tour "${review.tour_title}"?`)) return;
    setDeleting(true);
    try {
      await axios.delete(
        `http://localhost:8000/api/tours/reviews/me/${review.id}/`,
        { headers: { Authorization: `Bearer ${token()}` } }
      );
      onDeleted(review.id);
    } catch {
      alert('Xóa thất bại. Vui lòng thử lại.');
      setDeleting(false);
    }
  };

  const handleSave = async () => {
    if (!content.trim()) { alert('Nội dung không được để trống.'); return; }
    setSaving(true);
    try {
      const res = await axios.put(
        `http://localhost:8000/api/tours/reviews/me/${review.id}/`,
        { content, rating },
        { headers: { Authorization: `Bearer ${token()}` } }
      );
      onUpdated(res.data);
      setEditing(false);
    } catch {
      alert('Cập nhật thất bại. Vui lòng thử lại.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{
      background: 'white', borderRadius: '14px',
      border: '1px solid #e5e7eb', marginBottom: '16px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)', overflow: 'hidden',
      opacity: deleting ? 0.5 : 1, transition: 'opacity 0.3s',
    }}>
      {/* BANNER TÊN TOUR — nổi bật ở trên cùng */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea15, #764ba215)',
        borderBottom: '1px solid #e0e7ff',
        padding: '12px 20px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <img
            src={worldTourIcon}
            alt="Tour"
            style={{
            width: '24px',
            height: '24px',
            objectFit: 'contain',
                  }}
          />
          <div>
            <p style={{ fontSize: '11px', color: '#6b7280', margin: 0, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Tour đã đánh giá
            </p>
            <p style={{ fontSize: '15px', fontWeight: 700, color: '#1a202c', margin: 0 }}>
              {review.tour_title || 'Không rõ tên tour'}
            </p>
          </div>
        </div>

        {/* Nút 3 chấm */}
        {!editing && (
          <ThreeDotMenu
            onEdit={() => setEditing(true)}
            onDelete={handleDelete}
          />
        )}
      </div>

      {/* Nội dung card */}
      <div style={{ padding: '16px 20px' }}>
        {/* Ngày đánh giá */}
        <p style={{ fontSize: '12px', color: '#9ca3af', margin: '0 0 10px' }}>
          🗓 {new Date(review.created_at).toLocaleDateString('vi-VN', {
            day: '2-digit', month: '2-digit', year: 'numeric'
          })}
        </p>

        {/* Chế độ XEM */}
        {!editing && (
          <>
            <StarDisplay rating={review.rating} />
            <p style={{ marginTop: '10px', color: '#374151', fontSize: '14px', lineHeight: 1.7 }}>
              {review.content}
            </p>
          </>
        )}

        {/* Chế độ SỬA inline */}
        {editing && (
          <div style={{
            marginTop: '4px', padding: '16px',
            background: '#f8fafc', borderRadius: '10px',
            border: '1.5px solid #e0e7ff',
          }}>
            <p style={{ fontWeight: 600, fontSize: '14px', marginBottom: '8px', color: '#374151' }}>
              Chỉnh sửa đánh giá
            </p>
            <label style={{ fontSize: '13px', color: '#6b7280', fontWeight: 600 }}>Số sao</label>
            <StarInput value={rating} onChange={setRating} />

            <label style={{ fontSize: '13px', color: '#6b7280', fontWeight: 600 }}>Nội dung</label>
            <textarea
              value={content}
              onChange={e => setContent(e.target.value)}
              rows={4}
              style={{
                width: '100%', marginTop: '6px', padding: '10px 12px',
                border: '1.5px solid #e5e7eb', borderRadius: '8px',
                fontSize: '14px', resize: 'vertical',
                boxSizing: 'border-box', fontFamily: 'inherit', outline: 'none',
              }}
              onFocus={e => e.target.style.borderColor = '#7c3aed'}
              onBlur={e => e.target.style.borderColor = '#e5e7eb'}
            />
            <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
              <button
                onClick={handleSave} disabled={saving}
                style={{
                  padding: '9px 20px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white', border: 'none', borderRadius: '8px',
                  fontWeight: 600, fontSize: '14px', cursor: 'pointer',
                  opacity: saving ? 0.7 : 1,
                }}
              >{saving ? 'Đang lưu...' : '💾 Lưu thay đổi'}</button>

              <button
                onClick={() => { setContent(review.content); setRating(review.rating); setEditing(false); }}
                style={{
                  padding: '9px 20px', background: '#f1f5f9',
                  color: '#374151', border: 'none', borderRadius: '8px',
                  fontWeight: 600, fontSize: '14px', cursor: 'pointer',
                }}
              >Hủy</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function MyReviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/tours/reviews/me/', {
      headers: { Authorization: `Bearer ${token()}` }
    })
      .then(res => setReviews(res.data))
      .catch(() => setError('Không thể tải đánh giá. Vui lòng thử lại.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '60px', color: '#6b7280' }}>
      Đang tải đánh giá...
    </div>
  );

  if (error) return (
    <div style={{ textAlign: 'center', padding: '60px', color: '#ef4444' }}>
      {error}
    </div>
  );

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', padding: '8px 0' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700, color: '#1a202c', margin: 0 }}>
          Đánh giá của tôi
        </h2>
        <p style={{ color: '#6b7280', fontSize: '14px', marginTop: '4px' }}>
          {reviews.length > 0 ? `Bạn có ${reviews.length} đánh giá` : 'Bạn chưa có đánh giá nào'}
        </p>
      </div>

      {reviews.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '60px 20px',
          background: 'white', borderRadius: '14px', border: '1px solid #e5e7eb',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>⭐</div>
          <p style={{ fontWeight: 700, color: '#1a202c', fontSize: '16px' }}>Chưa có đánh giá nào</p>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>Hãy đặt tour và chia sẻ trải nghiệm của bạn!</p>
        </div>
      ) : (
        reviews.map(review => (
          <ReviewCard
            key={review.id}
            review={review}
            onDeleted={(id) => setReviews(prev => prev.filter(r => r.id !== id))}
            onUpdated={(updated) => setReviews(prev => prev.map(r => r.id === updated.id ? updated : r))}
          />
        ))
      )}
    </div>
  );
}