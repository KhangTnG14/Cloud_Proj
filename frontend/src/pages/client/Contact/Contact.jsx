import React, { useState } from 'react';
import address from '../../../assets/adress.png';
import phone from '../../../assets/phone-call.png';
import email from '../../../assets/email.png';
import clock from '../../../assets/hour.png';
import './Contact.css';

export default function Contact() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        alert('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong thời gian sớm nhất.');
        // Sau này bạn có thể kết nối với API backend
        setFormData({ name: '', email: '', phone: '', subject: '', message: '' });
    };

    return (
        <div className="contact-page">
            {/* Hero Section */}
            <div className="contact-hero">
                <h1>Liên Hệ Với Chúng Tôi</h1>
                <p>Chúng tôi luôn sẵn sàng hỗ trợ bạn có một chuyến đi tuyệt vời</p>
            </div>

            <div className="contact-container">
                {/* Thông tin liên hệ */}
                <div className="contact-info">
                    <h2>Thông Tin Liên Hệ</h2>
                    
                    <div className="info-card">
                        <div className="icon">
                            <img src={address} alt="Address" />
                        </div>
                        <div>
                            <h3>Địa chỉ</h3>
                            <p>12 Nguyễn Văn Bảo, Hạnh Thông, Hồ Chí Minh, Việt Nam</p>
                        </div>
                    </div>

                    <div className="info-card">
                        <div className="icon">
                            <img src={phone} alt="Phone" />
                        </div>
                        <div>
                            <h3>Hotline</h3>
                            <p><a href="tel:0862327xxx">0xxx xxx xxx</a></p>
                        </div>
                    </div>

                    <div className="info-card">
                        <div className="icon">
                            <img src={email} alt="Email" />
                        </div>
                        <div>
                            <h3>Email</h3>
                            <p><a href="mailto:h2kt_tourgo@gmail.com">h2kt-tourgo@gmail.com</a></p>
                        </div>
                    </div>

                    <div className="info-card">
                        <div className="icon">
                            <img src={clock} alt="Clock" />
                        </div>
                        <div>
                            <h3>Giờ làm việc</h3>
                            <p>Thứ 2 - Chủ Nhật: 07:30 - 21:30</p>
                        </div>
                    </div>
                </div>

                {/* Form liên hệ */}
                <div className="contact-form">
                    <h2>Gửi Tin Nhắn Cho Chúng Tôi</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label>Họ và tên</label>
                            <input 
                                type="text" 
                                name="name" 
                                value={formData.name}
                                onChange={handleChange}
                                required 
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Email</label>
                                <input 
                                    type="email" 
                                    name="email" 
                                    value={formData.email}
                                    onChange={handleChange}
                                    required 
                                />
                            </div>
                            <div className="form-group">
                                <label>Số điện thoại</label>
                                <input 
                                    type="tel" 
                                    name="phone" 
                                    value={formData.phone}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Tiêu đề</label>
                            <input 
                                type="text" 
                                name="subject" 
                                value={formData.subject}
                                onChange={handleChange}
                                required 
                            />
                        </div>

                        <div className="form-group">
                            <label>Nội dung</label>
                            <textarea 
                                name="message" 
                                rows="6"
                                value={formData.message}
                                onChange={handleChange}
                                required
                            ></textarea>
                        </div>

                        <button type="submit" className="submit-btn">
                            Gửi Tin Nhắn
                        </button>
                    </form>
                </div>
            </div>

            {/* Google Maps */}
            <div className="map-section">
                <h2>Vị Trí Của Chúng Tôi</h2>
                <div className="map-container">
                    <iframe
                        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3918.8582379826526!2d106.68427047480561!3d10.822158889329412!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3174deb3ef536f31%3A0x8b7bb8b7c956157b!2zVHLGsOG7nW5nIMSQ4bqhaSBo4buNYyBDw7RuZyBuZ2hp4buHcCBUUC5IQ00!5e0!3m2!1svi!2s!4v1779545548587!5m2!1svi!2s" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
                        width="100%"
                        height="450"
                        style={{ border: 0 }}
                        allowFullScreen=""
                        loading="lazy"
                    ></iframe>
                </div>
            </div>
        </div>
    );
}
